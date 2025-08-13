"""
LLM Integration Module

Handles local LLM integration for structured data extraction and procedural step identification.
"""

import logging
import json
from typing import List, Dict, Optional, Any
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from ctransformers import AutoModelForCausalLM as CTAutoModelForCausalLM
import re

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Handles local LLM processing for technical document analysis."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize LLM processor with configuration."""
        self.config = config or {}
        self.model_name = self.config.get('model_name', 'gpt2')
        self.max_length = self.config.get('max_length', 512)
        self.temperature = self.config.get('temperature', 0.7)
        self.use_ctransformers = self.config.get('use_ctransformers', True)
        
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        
        # Initialize model
        self._load_model()
        
        # Structured extraction prompts
        self.extraction_prompts = {
            'procedural_steps': """
Extract procedural steps from the following technical text. Return as JSON array with fields:
- step_number: sequential number
- description: step description
- estimated_time: estimated time to complete
- required_tools: list of required tools/equipment
- safety_notes: list of safety considerations
- dependencies: list of prerequisite steps

Text: {text}

JSON Output:
""",
            'modules': """
Identify logical modules from the following technical text. Return as JSON array with fields:
- module_id: unique identifier
- name: module name
- description: module description
- start_page: starting page number
- end_page: ending page number
- confidence: confidence score (0-1)

Text: {text}

JSON Output:
""",
            'decision_points': """
Extract decision points and conditional logic from the following technical text. Return as JSON array with fields:
- decision_id: unique identifier
- condition: the condition to check
- actions: list of actions to take
- priority: priority level (high/medium/low)
- fallback: fallback action if condition fails

Text: {text}

JSON Output:
""",
            'equipment': """
Extract equipment and tools mentioned in the following technical text. Return as JSON array with fields:
- equipment_id: unique identifier
- name: equipment name
- type: equipment type
- specifications: technical specifications
- maintenance_requirements: maintenance needs

Text: {text}

JSON Output:
"""
        }
        
    def _load_model(self):
        """Load the local LLM model."""
        try:
            if self.use_ctransformers:
                # Use ctransformers for optimized local inference
                self.model = CTAutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    model_type="gpt2",
                    lib="avx2",
                    gpu_layers=0  # CPU only for on-premise deployment
                )
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            else:
                # Use standard transformers
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    low_cpu_mem_usage=True
                )
                
                if torch.cuda.is_available():
                    self.model = self.model.cuda()
                    
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=self.max_length,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            logger.info(f"Successfully loaded LLM model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error loading LLM model: {e}")
            self.model = None
            self.tokenizer = None
            self.pipeline = None
    
    def extract_structured_data(self, text: str, extraction_type: str) -> List[Dict]:
        """
        Extract structured data using LLM.
        
        Args:
            text: Input text
            extraction_type: Type of extraction ('procedural_steps', 'modules', etc.)
            
        Returns:
            List of extracted structured data
        """
        if not self.pipeline:
            logger.warning("LLM model not available, using fallback extraction")
            return self._fallback_extraction(text, extraction_type)
        
        try:
            # Get appropriate prompt
            prompt_template = self.extraction_prompts.get(extraction_type)
            if not prompt_template:
                raise ValueError(f"Unknown extraction type: {extraction_type}")
            
            prompt = prompt_template.format(text=text[:1000])  # Limit text length
            
            # Generate response
            response = self.pipeline(prompt, max_length=self.max_length)[0]['generated_text']
            
            # Extract JSON from response
            json_data = self._extract_json_from_response(response)
            
            if json_data:
                return json_data
            else:
                logger.warning("Failed to extract JSON from LLM response, using fallback")
                return self._fallback_extraction(text, extraction_type)
                
        except Exception as e:
            logger.error(f"Error in LLM extraction: {e}")
            return self._fallback_extraction(text, extraction_type)
    
    def _extract_json_from_response(self, response: str) -> List[Dict]:
        """Extract JSON data from LLM response."""
        try:
            # Find JSON array in response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            
            # Try to find JSON object
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return [data] if isinstance(data, dict) else data
            
            return []
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {e}")
            return []
    
    def _fallback_extraction(self, text: str, extraction_type: str) -> List[Dict]:
        """Fallback extraction using rule-based methods."""
        if extraction_type == 'procedural_steps':
            return self._extract_steps_fallback(text)
        elif extraction_type == 'modules':
            return self._extract_modules_fallback(text)
        elif extraction_type == 'decision_points':
            return self._extract_decisions_fallback(text)
        elif extraction_type == 'equipment':
            return self._extract_equipment_fallback(text)
        else:
            return []
    
    def _extract_steps_fallback(self, text: str) -> List[Dict]:
        """Fallback procedural step extraction."""
        steps = []
        step_patterns = [
            r'\b(?:step|procedure)\s+(\d+)[\.:]?\s*([^.!?]+[.!?])',
            r'\b(\d+)[\.)]\s*([^.!?]+[.!?])',
        ]
        
        for pattern in step_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                step_num = match.group(1)
                description = match.group(2).strip()
                
                steps.append({
                    'step_number': int(step_num),
                    'description': description,
                    'estimated_time': '5 minutes',  # Default
                    'required_tools': [],
                    'safety_notes': [],
                    'dependencies': []
                })
        
        return steps
    
    def _extract_modules_fallback(self, text: str) -> List[Dict]:
        """Fallback module extraction."""
        modules = []
        module_patterns = [
            r'\n\s*(\d+\.\s*[A-Z][^.!?]*?)(?=\n)',
            r'\n\s*([A-Z][A-Z\s]{3,})(?=\n)',
        ]
        
        for i, pattern in enumerate(module_patterns):
            matches = re.finditer(pattern, text)
            for match in matches:
                modules.append({
                    'module_id': f'module_{i+1:03d}',
                    'name': match.group(1).strip(),
                    'description': f"Module {match.group(1).strip()}",
                    'start_page': 1,
                    'end_page': 1,
                    'confidence': 0.7
                })
        
        return modules
    
    def _extract_decisions_fallback(self, text: str) -> List[Dict]:
        """Fallback decision point extraction."""
        decisions = []
        decision_patterns = [
            r'\b(?:if|when)\s+([^.!?]+?)\s+(?:then|proceed)',
            r'\b(?:check|verify)\s+([^.!?]+?)\s+(?:before|prior)',
        ]
        
        for i, pattern in enumerate(decision_patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                decisions.append({
                    'decision_id': f'decision_{i+1:03d}',
                    'condition': match.group(1).strip(),
                    'actions': ['proceed', 'halt'],
                    'priority': 'medium',
                    'fallback': 'notify supervisor'
                })
        
        return decisions
    
    def _extract_equipment_fallback(self, text: str) -> List[Dict]:
        """Fallback equipment extraction."""
        equipment = []
        equipment_patterns = [
            r'\b([A-Z][A-Z0-9\-\s]{2,})\b',  # All caps identifiers
            r'\b([A-Z]{2,}\d{2,})\b',        # Model numbers
        ]
        
        for i, pattern in enumerate(equipment_patterns):
            matches = re.finditer(pattern, text)
            for match in matches:
                equipment.append({
                    'equipment_id': f'equipment_{i+1:03d}',
                    'name': match.group(1).strip(),
                    'type': 'unknown',
                    'specifications': '',
                    'maintenance_requirements': 'standard'
                })
        
        return equipment
    
    def analyze_text_complexity(self, text: str) -> Dict:
        """
        Analyze text complexity using LLM.
        
        Args:
            text: Input text
            
        Returns:
            Complexity analysis results
        """
        if not self.pipeline:
            return self._fallback_complexity_analysis(text)
        
        try:
            prompt = f"""
Analyze the complexity of the following technical text. Return as JSON with fields:
- readability_score: 0-100 scale
- technical_difficulty: low/medium/high
- domain_specific_terms: count of technical terms
- sentence_complexity: average sentence length
- overall_assessment: brief assessment

Text: {text[:500]}

JSON Output:
"""
            
            response = self.pipeline(prompt, max_length=200)[0]['generated_text']
            json_data = self._extract_json_from_response(response)
            
            if json_data and isinstance(json_data, list) and len(json_data) > 0:
                return json_data[0]
            else:
                return self._fallback_complexity_analysis(text)
                
        except Exception as e:
            logger.error(f"Error in complexity analysis: {e}")
            return self._fallback_complexity_analysis(text)
    
    def _fallback_complexity_analysis(self, text: str) -> Dict:
        """Fallback complexity analysis using basic metrics."""
        sentences = text.split('.')
        words = text.split()
        
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Count technical terms (simplified)
        technical_terms = len(re.findall(r'\b[A-Z][A-Z0-9\-\s]{2,}\b', text))
        
        return {
            'readability_score': max(0, 100 - avg_sentence_length * 2),
            'technical_difficulty': 'high' if technical_terms > 10 else 'medium' if technical_terms > 5 else 'low',
            'domain_specific_terms': technical_terms,
            'sentence_complexity': avg_sentence_length,
            'overall_assessment': 'Technical document with moderate complexity'
        }
    
    def generate_summary(self, text: str) -> str:
        """
        Generate a summary of the technical text.
        
        Args:
            text: Input text
            
        Returns:
            Generated summary
        """
        if not self.pipeline:
            return self._fallback_summary(text)
        
        try:
            prompt = f"""
Summarize the following technical text in 2-3 sentences:

{text[:800]}

Summary:
"""
            
            response = self.pipeline(prompt, max_length=150)[0]['generated_text']
            
            # Extract summary from response
            summary_match = re.search(r'Summary:\s*(.+)', response, re.DOTALL)
            if summary_match:
                return summary_match.group(1).strip()
            else:
                return self._fallback_summary(text)
                
        except Exception as e:
            logger.error(f"Error in summary generation: {e}")
            return self._fallback_summary(text)
    
    def _fallback_summary(self, text: str) -> str:
        """Fallback summary generation."""
        sentences = text.split('.')
        if len(sentences) >= 2:
            return '. '.join(sentences[:2]) + '.'
        else:
            return text[:200] + '...'
    
    def is_model_available(self) -> bool:
        """Check if LLM model is available."""
        return self.model is not None and self.pipeline is not None
