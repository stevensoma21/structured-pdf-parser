"""
Main Pipeline Module

Orchestrates the complete technical document processing pipeline.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from .agent import AgenticWorkflow
from .data_structurer import DataStructurer

logger = logging.getLogger(__name__)


class TechnicalDocPipeline:
    """Main pipeline for processing technical documents."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the technical document pipeline."""
        self.config = config or {}
        
        # Initialize components
        self.workflow = AgenticWorkflow(self.config)
        self.data_structurer = DataStructurer(self.config)
        
        # Setup logging
        self._setup_logging()
        
        logger.info("Technical Document Pipeline initialized")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def process_document(self, pdf_path: str, output_path: Optional[str] = None) -> Dict:
        """
        Process a single technical document.
        
        Args:
            pdf_path: Path to the PDF document
            output_path: Optional path to save results
            
        Returns:
            Processing results
        """
        logger.info(f"Processing document: {pdf_path}")
        
        try:
            # Process document through workflow
            results = self.workflow.process_document(pdf_path)
            
            # Structure the data
            structured_results = self.data_structurer.structure_results(results)
            
            # Add processing metadata
            structured_results['processing_metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'pipeline_version': '1.0.0',
                'processing_time': results.get('processing_time', 0),
                'success': len(results.get('errors', [])) == 0
            }
            
            # Save results if output path provided
            if output_path:
                self._save_results(structured_results, output_path)
            
            logger.info(f"Document processing completed: {pdf_path}")
            return structured_results
            
        except Exception as e:
            logger.error(f"Error processing document {pdf_path}: {e}")
            return {
                'document_info': {
                    'filename': pdf_path,
                    'processing_timestamp': datetime.now().isoformat(),
                    'confidence_score': 0.0
                },
                'errors': [str(e)],
                'processing_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'pipeline_version': '1.0.0',
                    'success': False
                }
            }
    
    def process_directory(self, input_dir: str, output_dir: str) -> List[Dict]:
        """
        Process all PDF documents in a directory.
        
        Args:
            input_dir: Directory containing PDF files
            output_dir: Directory to save results
            
        Returns:
            List of processing results
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all PDF files
        pdf_files = list(input_path.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        results = []
        for pdf_file in pdf_files:
            output_file = output_path / f"{pdf_file.stem}_results.json"
            result = self.process_document(str(pdf_file), str(output_file))
            results.append(result)
        
        # Generate summary report
        summary = self._generate_summary_report(results)
        summary_path = output_path / "processing_summary.json"
        self._save_results(summary, str(summary_path))
        
        logger.info(f"Directory processing completed. Processed {len(results)} files.")
        return results
    
    def _save_results(self, results: Dict, output_path: str):
        """Save results to JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving results to {output_path}: {e}")
    
    def _generate_summary_report(self, results: List[Dict]) -> Dict:
        """Generate a summary report of processing results."""
        total_files = len(results)
        successful_files = sum(1 for r in results if r.get('processing_metadata', {}).get('success', False))
        
        avg_confidence = sum(
            r.get('document_info', {}).get('confidence_score', 0) 
            for r in results
        ) / total_files if total_files > 0 else 0
        
        total_modules = sum(len(r.get('modules', [])) for r in results)
        total_steps = sum(len(r.get('procedural_steps', [])) for r in results)
        total_decisions = sum(len(r.get('decision_points', [])) for r in results)
        
        return {
            'summary': {
                'total_files_processed': total_files,
                'successful_files': successful_files,
                'failed_files': total_files - successful_files,
                'success_rate': successful_files / total_files if total_files > 0 else 0,
                'average_confidence': avg_confidence
            },
            'extraction_stats': {
                'total_modules_extracted': total_modules,
                'total_procedural_steps': total_steps,
                'total_decision_points': total_decisions,
                'average_modules_per_file': total_modules / total_files if total_files > 0 else 0,
                'average_steps_per_file': total_steps / total_files if total_files > 0 else 0
            },
            'processing_timestamp': datetime.now().isoformat(),
            'pipeline_version': '1.0.0'
        }
    
    def get_processing_status(self) -> Dict:
        """Get the current processing status and system health."""
        return {
            'pipeline_status': 'ready',
            'components': {
                'pdf_processor': 'available',
                'nlp_processor': 'available',
                'llm_processor': 'available' if self.workflow.llm_processor.is_model_available() else 'unavailable',
                'agentic_workflow': 'ready'
            },
            'system_info': {
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def validate_configuration(self) -> Dict:
        """Validate the pipeline configuration."""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required components
        if not hasattr(self.workflow, 'pdf_processor'):
            validation_results['valid'] = False
            validation_results['errors'].append("PDF processor not initialized")
        
        if not hasattr(self.workflow, 'nlp_processor'):
            validation_results['valid'] = False
            validation_results['errors'].append("NLP processor not initialized")
        
        # Check LLM availability
        if not self.workflow.llm_processor.is_model_available():
            validation_results['warnings'].append("LLM model not available - will use fallback methods")
        
        # Check configuration parameters
        required_config_keys = ['confidence_thresholds', 'log_level']
        for key in required_config_keys:
            if key not in self.config:
                validation_results['warnings'].append(f"Missing configuration key: {key}")
        
        return validation_results
