"""
Agentic Workflow Module

Handles multi-step reasoning, model selection, and decision orchestration for the ML pipeline.
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import json
from dataclasses import dataclass
from .pdf_processor import PDFProcessor
from .nlp_processor import NLPProcessor
from .llm_processor import LLMProcessor
import re

logger = logging.getLogger(__name__)


class ProcessingStage(Enum):
    """Enumeration of processing stages."""
    PDF_EXTRACTION = "pdf_extraction"
    TEXT_CLEANING = "text_cleaning"
    NLP_ANALYSIS = "nlp_analysis"
    LLM_PROCESSING = "llm_processing"
    STRUCTURING = "structuring"
    VALIDATION = "validation"


class ConfidenceLevel(Enum):
    """Enumeration of confidence levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ProcessingResult:
    """Data class for processing results."""
    stage: ProcessingStage
    success: bool
    confidence: float
    data: Any
    metadata: Dict
    errors: List[str]


class AgenticWorkflow:
    """Handles agentic workflow for technical document processing."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize agentic workflow with configuration."""
        self.config = config or {}
        self.confidence_thresholds = self.config.get('confidence_thresholds', {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        })
        
        # Initialize processors
        self.pdf_processor = PDFProcessor(self.config.get('pdf_processor', {}))
        self.nlp_processor = NLPProcessor(self.config.get('nlp_processor', {}))
        self.llm_processor = LLMProcessor(self.config.get('llm_processor', {}))
        
        # Processing history
        self.processing_history = []
        
        # Decision rules
        self.decision_rules = self._initialize_decision_rules()
        
    def _initialize_decision_rules(self) -> Dict:
        """Initialize decision rules for model selection and fallback logic."""
        return {
            'text_quality_assessment': {
                'high_quality': {
                    'min_length': 1000,
                    'max_noise_ratio': 0.1,
                    'min_confidence': 0.8
                },
                'medium_quality': {
                    'min_length': 500,
                    'max_noise_ratio': 0.2,
                    'min_confidence': 0.6
                },
                'low_quality': {
                    'min_length': 100,
                    'max_noise_ratio': 0.5,
                    'min_confidence': 0.3
                }
            },
            'model_selection': {
                'llm_required': ['procedural_steps', 'modules', 'decision_points'],
                'nlp_required': ['entities', 'dependencies', 'classification'],
                'fallback_required': ['low_confidence', 'model_unavailable']
            },
            'fallback_strategies': {
                'llm_fallback': 'rule_based_extraction',
                'nlp_fallback': 'pattern_matching',
                'pdf_fallback': 'ocr_processing'
            }
        }
    
    def process_document(self, pdf_path: str) -> Dict:
        """
        Process a technical document through the complete pipeline.
        
        Args:
            pdf_path: Path to the PDF document
            
        Returns:
            Complete processing results
        """
        logger.info(f"Starting document processing: {pdf_path}")
        
        # Initialize results
        results = {
            'document_info': {
                'filename': pdf_path,
                'processing_timestamp': None,
                'confidence_score': 0.0
            },
            'processing_stages': [],
            'modules': [],
            'procedural_steps': [],
            'decision_points': [],
            'equipment': [],
            'summary': '',
            'errors': []
        }
        
        try:
            # Stage 1: PDF Extraction
            pdf_result = self._process_pdf_extraction(pdf_path)
            results['processing_stages'].append(pdf_result)
            
            if not pdf_result.success:
                raise Exception(f"PDF extraction failed: {pdf_result.errors}")
            
            # Stage 2: Text Quality Assessment
            quality_result = self._assess_text_quality(pdf_result.data)
            results['processing_stages'].append(quality_result)
            
            # Stage 3: NLP Analysis
            nlp_result = self._process_nlp_analysis(pdf_result.data, quality_result.data)
            results['processing_stages'].append(nlp_result)
            
            # Stage 4: LLM Processing
            llm_result = self._process_llm_analysis(pdf_result.data, quality_result.data)
            results['processing_stages'].append(llm_result)
            
            # Stage 5: Data Structuring
            structure_result = self._structure_data(nlp_result.data, llm_result.data)
            results['processing_stages'].append(structure_result)
            
            # Stage 6: Validation
            validation_result = self._validate_results(structure_result.data)
            results['processing_stages'].append(validation_result)
            
            # Compile final results
            results.update(structure_result.data)
            results['document_info']['confidence_score'] = validation_result.confidence
            results['summary'] = self.llm_processor.generate_summary(pdf_result.data['full_text'])
            
            logger.info(f"Document processing completed successfully with confidence: {validation_result.confidence}")
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            results['errors'].append(str(e))
            results['document_info']['confidence_score'] = 0.0
        
        return results
    
    def _process_pdf_extraction(self, pdf_path: str) -> ProcessingResult:
        """Process PDF extraction stage."""
        try:
            # Extract text from PDF
            text_data = self.pdf_processor.extract_text(pdf_path)
            
            # Segment document
            text_data = self.pdf_processor.segment_document(text_data)
            
            # Extract tables
            tables = self.pdf_processor.extract_tables(pdf_path)
            text_data['tables'] = tables
            
            confidence = self._calculate_extraction_confidence(text_data)
            
            return ProcessingResult(
                stage=ProcessingStage.PDF_EXTRACTION,
                success=True,
                confidence=confidence,
                data=text_data,
                metadata={'extraction_method': text_data.get('extraction_method', 'unknown')},
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ProcessingResult(
                stage=ProcessingStage.PDF_EXTRACTION,
                success=False,
                confidence=0.0,
                data={},
                metadata={},
                errors=[str(e)]
            )
    
    def _assess_text_quality(self, text_data: Dict) -> ProcessingResult:
        """Assess text quality and determine processing strategy."""
        try:
            text = text_data.get('full_text', '')
            
            # Calculate quality metrics
            quality_metrics = {
                'length': len(text),
                'noise_ratio': self._calculate_noise_ratio(text),
                'structure_score': self._calculate_structure_score(text),
                'technical_term_density': self._calculate_technical_term_density(text)
            }
            
            # Determine quality level
            quality_level = self._determine_quality_level(quality_metrics)
            
            # Determine processing strategy
            processing_strategy = self._determine_processing_strategy(quality_level, quality_metrics)
            
            confidence = min(quality_metrics['structure_score'], 0.9)
            
            return ProcessingResult(
                stage=ProcessingStage.TEXT_CLEANING,
                success=True,
                confidence=confidence,
                data={
                    'quality_level': quality_level,
                    'quality_metrics': quality_metrics,
                    'processing_strategy': processing_strategy
                },
                metadata={'text_length': len(text)},
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Text quality assessment failed: {e}")
            return ProcessingResult(
                stage=ProcessingStage.TEXT_CLEANING,
                success=False,
                confidence=0.0,
                data={},
                metadata={},
                errors=[str(e)]
            )
    
    def _process_nlp_analysis(self, text_data: Dict, quality_data: Dict) -> ProcessingResult:
        """Process NLP analysis stage."""
        try:
            text = text_data.get('full_text', '')
            strategy = quality_data.get('processing_strategy', {})
            
            nlp_results = {}
            
            # Extract entities
            if strategy.get('extract_entities', True):
                nlp_results['entities'] = self.nlp_processor.extract_entities(text)
                nlp_results['technical_entities'] = self.nlp_processor.extract_technical_entities(text)
            
            # Extract procedural steps
            if strategy.get('extract_steps', True):
                nlp_results['procedural_steps'] = self.nlp_processor.extract_procedural_steps(text)
            
            # Extract modules
            if strategy.get('extract_modules', True):
                nlp_results['modules'] = self.nlp_processor.extract_modules(text)
            
            # Extract decision points
            if strategy.get('extract_decisions', True):
                nlp_results['decision_points'] = self.nlp_processor.extract_decision_points(text)
            
            # Perform dependency parsing
            if strategy.get('dependency_parsing', True):
                nlp_results['dependencies'] = self.nlp_processor.perform_dependency_parsing(text)
            
            # Classify text
            if strategy.get('classification', True):
                nlp_results['classification'] = self.nlp_processor.classify_text(text)
            
            confidence = self._calculate_nlp_confidence(nlp_results)
            
            return ProcessingResult(
                stage=ProcessingStage.NLP_ANALYSIS,
                success=True,
                confidence=confidence,
                data=nlp_results,
                metadata={'strategy': strategy},
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"NLP analysis failed: {e}")
            return ProcessingResult(
                stage=ProcessingStage.NLP_ANALYSIS,
                success=False,
                confidence=0.0,
                data={},
                metadata={},
                errors=[str(e)]
            )
    
    def _process_llm_analysis(self, text_data: Dict, quality_data: Dict) -> ProcessingResult:
        """Process LLM analysis stage."""
        try:
            text = text_data.get('full_text', '')
            strategy = quality_data.get('processing_strategy', {})
            
            llm_results = {}
            
            # Check if LLM is available and should be used
            if self.llm_processor.is_model_available() and strategy.get('use_llm', True):
                # Extract structured data using LLM
                for extraction_type in ['procedural_steps', 'modules', 'decision_points', 'equipment']:
                    if strategy.get(f'extract_{extraction_type}', True):
                        llm_results[extraction_type] = self.llm_processor.extract_structured_data(
                            text, extraction_type
                        )
                
                # Analyze complexity
                llm_results['complexity_analysis'] = self.llm_processor.analyze_text_complexity(text)
            else:
                logger.info("LLM not available or disabled, using fallback methods")
                llm_results = self._fallback_llm_processing(text, strategy)
            
            confidence = self._calculate_llm_confidence(llm_results)
            
            return ProcessingResult(
                stage=ProcessingStage.LLM_PROCESSING,
                success=True,
                confidence=confidence,
                data=llm_results,
                metadata={'llm_available': self.llm_processor.is_model_available()},
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return ProcessingResult(
                stage=ProcessingStage.LLM_PROCESSING,
                success=False,
                confidence=0.0,
                data={},
                metadata={},
                errors=[str(e)]
            )
    
    def _structure_data(self, nlp_data: Dict, llm_data: Dict) -> ProcessingResult:
        """Structure and combine data from different processors."""
        try:
            structured_data = {
                'modules': [],
                'procedural_steps': [],
                'decision_points': [],
                'equipment': []
            }
            
            # Combine and prioritize data sources
            # LLM data takes precedence if available and high confidence
            for key in structured_data.keys():
                if key in llm_data and llm_data[key]:
                    structured_data[key] = llm_data[key]
                elif key in nlp_data and nlp_data[key]:
                    structured_data[key] = self._convert_nlp_to_structured(nlp_data[key], key)
            
            # Add metadata
            structured_data['metadata'] = {
                'nlp_entities': nlp_data.get('entities', []),
                'technical_entities': nlp_data.get('technical_entities', []),
                'classification': nlp_data.get('classification', {}),
                'complexity_analysis': llm_data.get('complexity_analysis', {})
            }
            
            confidence = self._calculate_structuring_confidence(structured_data)
            
            return ProcessingResult(
                stage=ProcessingStage.STRUCTURING,
                success=True,
                confidence=confidence,
                data=structured_data,
                metadata={'data_sources': ['nlp', 'llm']},
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Data structuring failed: {e}")
            return ProcessingResult(
                stage=ProcessingStage.STRUCTURING,
                success=False,
                confidence=0.0,
                data={},
                metadata={},
                errors=[str(e)]
            )
    
    def _validate_results(self, structured_data: Dict) -> ProcessingResult:
        """Validate final results."""
        try:
            validation_errors = []
            confidence_factors = []
            
            # Validate modules
            if structured_data.get('modules'):
                confidence_factors.append(0.8)
            else:
                validation_errors.append("No modules identified")
                confidence_factors.append(0.2)
            
            # Validate procedural steps
            if structured_data.get('procedural_steps'):
                confidence_factors.append(0.9)
            else:
                validation_errors.append("No procedural steps identified")
                confidence_factors.append(0.1)
            
            # Validate decision points
            if structured_data.get('decision_points'):
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)  # Decision points are optional
            
            # Calculate overall confidence
            confidence = sum(confidence_factors) / len(confidence_factors)
            
            return ProcessingResult(
                stage=ProcessingStage.VALIDATION,
                success=len(validation_errors) == 0,
                confidence=confidence,
                data=structured_data,
                metadata={'validation_errors': validation_errors},
                errors=validation_errors
            )
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return ProcessingResult(
                stage=ProcessingStage.VALIDATION,
                success=False,
                confidence=0.0,
                data={},
                metadata={},
                errors=[str(e)]
            )
    
    def _calculate_extraction_confidence(self, text_data: Dict) -> float:
        """Calculate confidence for PDF extraction."""
        confidence = 0.5  # Base confidence
        
        # Adjust based on extraction method
        method = text_data.get('extraction_method', 'unknown')
        if method == 'pymupdf':
            confidence += 0.3
        elif method == 'pdfplumber':
            confidence += 0.2
        elif method == 'ocr':
            confidence += 0.1
        
        # Adjust based on text length
        text_length = len(text_data.get('full_text', ''))
        if text_length > 1000:
            confidence += 0.1
        elif text_length < 100:
            confidence -= 0.2
        
        return min(confidence, 1.0)
    
    def _calculate_noise_ratio(self, text: str) -> float:
        """Calculate noise ratio in text."""
        # Simple noise detection based on special characters
        special_chars = len(re.findall(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', text))
        total_chars = len(text)
        return special_chars / total_chars if total_chars > 0 else 0.0
    
    def _calculate_structure_score(self, text: str) -> float:
        """Calculate structure score based on formatting."""
        # Count structured elements
        structured_elements = len(re.findall(r'\n\s*\d+\.\s*', text))
        structured_elements += len(re.findall(r'\n\s*[A-Z][A-Z\s]{3,}\n', text))
        
        # Normalize by text length
        text_length = len(text)
        return min(structured_elements / (text_length / 1000), 1.0) if text_length > 0 else 0.0
    
    def _calculate_technical_term_density(self, text: str) -> float:
        """Calculate technical term density."""
        technical_terms = len(re.findall(r'\b[A-Z][A-Z0-9\-\s]{2,}\b', text))
        words = text.split()
        return technical_terms / len(words) if words else 0.0
    
    def _determine_quality_level(self, metrics: Dict) -> str:
        """Determine text quality level."""
        if (metrics['length'] >= 1000 and 
            metrics['noise_ratio'] <= 0.1 and 
            metrics['structure_score'] >= 0.5):
            return 'high'
        elif (metrics['length'] >= 500 and 
              metrics['noise_ratio'] <= 0.2 and 
              metrics['structure_score'] >= 0.3):
            return 'medium'
        else:
            return 'low'
    
    def _determine_processing_strategy(self, quality_level: str, metrics: Dict) -> Dict:
        """Determine processing strategy based on quality level."""
        strategy = {
            'use_llm': quality_level in ['high', 'medium'],
            'extract_entities': True,
            'extract_steps': True,
            'extract_modules': True,
            'extract_decisions': True,
            'dependency_parsing': quality_level == 'high',
            'classification': True
        }
        
        # Adjust strategy based on metrics
        if metrics['technical_term_density'] > 0.1:
            strategy['extract_entities'] = True
        
        return strategy
    
    def _calculate_nlp_confidence(self, nlp_results: Dict) -> float:
        """Calculate confidence for NLP analysis."""
        confidence = 0.5  # Base confidence
        
        # Adjust based on results
        if nlp_results.get('entities'):
            confidence += 0.1
        if nlp_results.get('procedural_steps'):
            confidence += 0.2
        if nlp_results.get('modules'):
            confidence += 0.1
        if nlp_results.get('classification'):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_llm_confidence(self, llm_results: Dict) -> float:
        """Calculate confidence for LLM analysis."""
        if not self.llm_processor.is_model_available():
            return 0.3  # Low confidence for fallback methods
        
        confidence = 0.6  # Base confidence for LLM
        
        # Adjust based on results
        for key in ['procedural_steps', 'modules', 'decision_points']:
            if llm_results.get(key):
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_structuring_confidence(self, structured_data: Dict) -> float:
        """Calculate confidence for data structuring."""
        confidence = 0.5  # Base confidence
        
        # Adjust based on structured data quality
        for key in ['modules', 'procedural_steps', 'decision_points']:
            if structured_data.get(key):
                confidence += 0.15
        
        return min(confidence, 1.0)
    
    def _fallback_llm_processing(self, text: str, strategy: Dict) -> Dict:
        """Fallback processing when LLM is not available."""
        return {
            'procedural_steps': self.nlp_processor.extract_procedural_steps(text),
            'modules': self.nlp_processor.extract_modules(text),
            'decision_points': self.nlp_processor.extract_decision_points(text),
            'equipment': self.nlp_processor.extract_technical_entities(text),
            'complexity_analysis': {
                'readability_score': 70,
                'technical_difficulty': 'medium',
                'domain_specific_terms': len(re.findall(r'\b[A-Z][A-Z0-9\-\s]{2,}\b', text)),
                'sentence_complexity': len(text.split()) / len(text.split('.')),
                'overall_assessment': 'Technical document processed with fallback methods'
            }
        }
    
    def _convert_nlp_to_structured(self, nlp_data: List[Dict], data_type: str) -> List[Dict]:
        """Convert NLP data to structured format."""
        if data_type == 'procedural_steps':
            return [
                {
                    'step_number': i + 1,
                    'description': item.get('text', ''),
                    'estimated_time': '5 minutes',
                    'required_tools': [],
                    'safety_notes': [],
                    'dependencies': []
                }
                for i, item in enumerate(nlp_data)
            ]
        elif data_type == 'modules':
            return [
                {
                    'module_id': f'module_{i+1:03d}',
                    'name': item.get('title', ''),
                    'description': item.get('content', '')[:200] + '...',
                    'start_page': 1,
                    'end_page': 1,
                    'confidence': item.get('confidence', 0.7)
                }
                for i, item in enumerate(nlp_data)
            ]
        elif data_type == 'decision_points':
            return [
                {
                    'decision_id': f'decision_{i+1:03d}',
                    'condition': item.get('condition', ''),
                    'actions': ['proceed', 'halt'],
                    'priority': 'medium',
                    'fallback': 'notify supervisor'
                }
                for i, item in enumerate(nlp_data)
            ]
        else:
            return nlp_data
