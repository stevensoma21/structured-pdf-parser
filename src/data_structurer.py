"""
Data Structurer Module

Handles JSON output formatting, module identification, and procedural step extraction.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class DataStructurer:
    """Handles structuring and formatting of extracted data."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize data structurer with configuration."""
        self.config = config or {}
        self.output_format = self.config.get('output_format', 'json')
        self.include_metadata = self.config.get('include_metadata', True)
        self.include_raw_data = self.config.get('include_raw_data', False)
        
    def structure_results(self, results: Dict) -> Dict:
        """
        Structure the processing results into the final output format.
        
        Args:
            results: Raw processing results
            
        Returns:
            Structured results in the specified format
        """
        try:
            structured_results = {
                'document_info': self._structure_document_info(results),
                'modules': self._structure_modules(results.get('modules', [])),
                'procedural_steps': self._structure_procedural_steps(results.get('procedural_steps', [])),
                'decision_points': self._structure_decision_points(results.get('decision_points', [])),
                'equipment': self._structure_equipment(results.get('equipment', [])),
                'summary': results.get('summary', ''),
                'errors': results.get('errors', [])
            }
            
            # Add metadata if requested
            if self.include_metadata:
                structured_results['metadata'] = self._structure_metadata(results)
            
            # Add raw data if requested
            if self.include_raw_data:
                structured_results['raw_data'] = self._structure_raw_data(results)
            
            return structured_results
            
        except Exception as e:
            logger.error(f"Error structuring results: {e}")
            return {
                'document_info': {
                    'filename': results.get('document_info', {}).get('filename', 'unknown'),
                    'processing_timestamp': datetime.now().isoformat(),
                    'confidence_score': 0.0
                },
                'errors': [str(e)],
                'modules': [],
                'procedural_steps': [],
                'decision_points': [],
                'equipment': []
            }
    
    def _structure_document_info(self, results: Dict) -> Dict:
        """Structure document information."""
        doc_info = results.get('document_info', {})
        
        return {
            'filename': doc_info.get('filename', 'unknown'),
            'processing_timestamp': doc_info.get('processing_timestamp') or datetime.now().isoformat(),
            'confidence_score': doc_info.get('confidence_score', 0.0),
            'extraction_method': doc_info.get('extraction_method', 'unknown'),
            'document_type': self._infer_document_type(results),
            'page_count': self._extract_page_count(results),
            'word_count': self._extract_word_count(results)
        }
    
    def _structure_modules(self, modules: List[Dict]) -> List[Dict]:
        """Structure module information."""
        structured_modules = []
        
        for i, module in enumerate(modules):
            structured_module = {
                'id': module.get('module_id') or f'module_{i+1:03d}',
                'name': module.get('name', ''),
                'description': module.get('description', ''),
                'confidence': module.get('confidence', 0.7),
                'start_page': module.get('start_page', 1),
                'end_page': module.get('end_page', 1),
                'content_length': len(module.get('content', '')),
                'sub_modules': self._extract_sub_modules(module),
                'keywords': self._extract_keywords(module.get('content', ''))
            }
            structured_modules.append(structured_module)
        
        return structured_modules
    
    def _structure_procedural_steps(self, steps: List[Dict]) -> List[Dict]:
        """Structure procedural step information."""
        structured_steps = []
        
        for i, step in enumerate(steps):
            structured_step = {
                'id': step.get('id') or f'step_{i+1:03d}',
                'module_id': step.get('module_id', ''),
                'step_number': step.get('step_number', i + 1),
                'description': step.get('description', ''),
                'sequence': step.get('sequence', i + 1),
                'dependencies': step.get('dependencies', []),
                'estimated_time': step.get('estimated_time', '5 minutes'),
                'required_tools': step.get('required_tools', []),
                'safety_notes': step.get('safety_notes', []),
                'warnings': self._extract_warnings(step.get('description', '')),
                'complexity': self._assess_step_complexity(step),
                'validation_checks': self._extract_validation_checks(step.get('description', ''))
            }
            structured_steps.append(structured_step)
        
        return structured_steps
    
    def _structure_decision_points(self, decisions: List[Dict]) -> List[Dict]:
        """Structure decision point information."""
        structured_decisions = []
        
        for i, decision in enumerate(decisions):
            structured_decision = {
                'id': decision.get('decision_id') or f'decision_{i+1:03d}',
                'description': decision.get('description', ''),
                'condition': decision.get('condition', ''),
                'actions': decision.get('actions', []),
                'priority': decision.get('priority', 'medium'),
                'fallback': decision.get('fallback', 'notify supervisor'),
                'triggers': self._extract_triggers(decision.get('condition', '')),
                'consequences': self._extract_consequences(decision.get('actions', [])),
                'risk_level': self._assess_risk_level(decision),
                'required_approval': self._requires_approval(decision)
            }
            structured_decisions.append(structured_decision)
        
        return structured_decisions
    
    def _structure_equipment(self, equipment: List[Dict]) -> List[Dict]:
        """Structure equipment information."""
        structured_equipment = []
        
        for i, item in enumerate(equipment):
            structured_item = {
                'id': item.get('equipment_id') or f'equipment_{i+1:03d}',
                'name': item.get('name', ''),
                'type': item.get('type', 'unknown'),
                'specifications': item.get('specifications', ''),
                'maintenance_requirements': item.get('maintenance_requirements', 'standard'),
                'calibration_needed': self._requires_calibration(item),
                'safety_classification': self._classify_safety_level(item),
                'operational_limits': self._extract_operational_limits(item),
                'replacement_schedule': self._extract_replacement_schedule(item)
            }
            structured_equipment.append(structured_item)
        
        return structured_equipment
    
    def _structure_metadata(self, results: Dict) -> Dict:
        """Structure metadata information."""
        return {
            'processing_stages': self._structure_processing_stages(results.get('processing_stages', [])),
            'quality_metrics': self._extract_quality_metrics(results),
            'technical_entities': results.get('metadata', {}).get('technical_entities', []),
            'classification': results.get('metadata', {}).get('classification', {}),
            'complexity_analysis': results.get('metadata', {}).get('complexity_analysis', {}),
            'extraction_confidence': self._calculate_overall_confidence(results)
        }
    
    def _structure_raw_data(self, results: Dict) -> Dict:
        """Structure raw data for debugging purposes."""
        return {
            'full_text': results.get('full_text', ''),
            'extracted_entities': results.get('metadata', {}).get('nlp_entities', []),
            'processing_stages': results.get('processing_stages', []),
            'original_results': results
        }
    
    def _infer_document_type(self, results: Dict) -> str:
        """Infer the type of technical document."""
        text = results.get('full_text', '').lower()
        
        if any(word in text for word in ['maintenance', 'repair', 'service']):
            return 'maintenance_manual'
        elif any(word in text for word in ['safety', 'procedure', 'protocol']):
            return 'safety_procedure'
        elif any(word in text for word in ['operation', 'manual', 'instruction']):
            return 'operation_manual'
        elif any(word in text for word in ['troubleshooting', 'diagnostic']):
            return 'troubleshooting_guide'
        else:
            return 'technical_document'
    
    def _extract_page_count(self, results: Dict) -> int:
        """Extract page count from results."""
        pages = results.get('pages', [])
        return len(pages) if pages else 1
    
    def _extract_word_count(self, results: Dict) -> int:
        """Extract word count from results."""
        text = results.get('full_text', '')
        return len(text.split()) if text else 0
    
    def _extract_sub_modules(self, module: Dict) -> List[str]:
        """Extract sub-modules from module content."""
        content = module.get('content', '')
        sub_modules = re.findall(r'\n\s*\d+\.\d+\s+([^.!?]+)', content)
        return sub_modules[:5]  # Limit to first 5 sub-modules
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content."""
        # Simple keyword extraction based on capitalization and technical terms
        keywords = re.findall(r'\b[A-Z][A-Z0-9\-\s]{2,}\b', content)
        return list(set(keywords))[:10]  # Limit to 10 unique keywords
    
    def _extract_warnings(self, description: str) -> List[str]:
        """Extract warnings from step description."""
        warnings = []
        warning_patterns = [
            r'\b(?:warning|caution|danger|hazard)\s*:?\s*([^.!?]+)',
            r'\b(?:do not|never|avoid|prevent)\s+([^.!?]+)',
        ]
        
        for pattern in warning_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            warnings.extend(matches)
        
        return warnings
    
    def _assess_step_complexity(self, step: Dict) -> str:
        """Assess the complexity of a procedural step."""
        description = step.get('description', '')
        
        # Count technical terms and measurements
        technical_terms = len(re.findall(r'\b[A-Z][A-Z0-9\-\s]{2,}\b', description))
        measurements = len(re.findall(r'\b\d+\.?\d*\s*(?:mm|cm|m|km|in|ft|yd|psi|bar|pa|kpa|mpa|volts?|v|amperes?|a|watts?|w|ohms?|Ω|degrees?|°|fahrenheit|f|celsius|c|kelvin|k)\b', description, re.IGNORECASE))
        
        total_complexity = technical_terms + measurements
        
        if total_complexity > 5:
            return 'high'
        elif total_complexity > 2:
            return 'medium'
        else:
            return 'low'
    
    def _extract_validation_checks(self, description: str) -> List[str]:
        """Extract validation checks from step description."""
        checks = []
        check_patterns = [
            r'\b(?:verify|check|confirm|validate|test)\s+([^.!?]+)',
            r'\b(?:ensure|make sure|confirm that)\s+([^.!?]+)',
        ]
        
        for pattern in check_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            checks.extend(matches)
        
        return checks
    
    def _extract_triggers(self, condition: str) -> List[str]:
        """Extract triggers from decision condition."""
        triggers = []
        trigger_patterns = [
            r'\b(?:if|when|whereas)\s+([^.!?]+)',
            r'\b(?:detect|identify|find)\s+([^.!?]+)',
        ]
        
        for pattern in trigger_patterns:
            matches = re.findall(pattern, condition, re.IGNORECASE)
            triggers.extend(matches)
        
        return triggers
    
    def _extract_consequences(self, actions: List[str]) -> List[str]:
        """Extract consequences from decision actions."""
        consequences = []
        for action in actions:
            if any(word in action.lower() for word in ['stop', 'halt', 'emergency', 'shutdown']):
                consequences.append('critical_stop')
            elif any(word in action.lower() for word in ['notify', 'alert', 'report']):
                consequences.append('notification_required')
            elif any(word in action.lower() for word in ['continue', 'proceed']):
                consequences.append('continue_operation')
        
        return consequences
    
    def _assess_risk_level(self, decision: Dict) -> str:
        """Assess the risk level of a decision point."""
        condition = decision.get('condition', '').lower()
        actions = [action.lower() for action in decision.get('actions', [])]
        
        high_risk_keywords = ['emergency', 'danger', 'hazard', 'critical', 'failure']
        medium_risk_keywords = ['warning', 'caution', 'attention', 'check']
        
        if any(keyword in condition for keyword in high_risk_keywords):
            return 'high'
        elif any(keyword in condition for keyword in medium_risk_keywords):
            return 'medium'
        else:
            return 'low'
    
    def _requires_approval(self, decision: Dict) -> bool:
        """Determine if decision requires approval."""
        condition = decision.get('condition', '').lower()
        actions = [action.lower() for action in decision.get('actions', [])]
        
        approval_keywords = ['supervisor', 'manager', 'authority', 'approval', 'permission']
        
        return any(keyword in condition for keyword in approval_keywords) or \
               any(keyword in action for action in actions for keyword in approval_keywords)
    
    def _requires_calibration(self, equipment: Dict) -> bool:
        """Determine if equipment requires calibration."""
        specs = equipment.get('specifications', '').lower()
        maintenance = equipment.get('maintenance_requirements', '').lower()
        
        calibration_keywords = ['calibrate', 'calibration', 'accuracy', 'precision']
        
        return any(keyword in specs for keyword in calibration_keywords) or \
               any(keyword in maintenance for keyword in calibration_keywords)
    
    def _classify_safety_level(self, equipment: Dict) -> str:
        """Classify equipment safety level."""
        name = equipment.get('name', '').lower()
        specs = equipment.get('specifications', '').lower()
        
        high_safety_keywords = ['safety', 'emergency', 'critical', 'protective']
        medium_safety_keywords = ['warning', 'caution', 'attention']
        
        if any(keyword in name for keyword in high_safety_keywords) or \
           any(keyword in specs for keyword in high_safety_keywords):
            return 'high'
        elif any(keyword in name for keyword in medium_safety_keywords) or \
             any(keyword in specs for keyword in medium_safety_keywords):
            return 'medium'
        else:
            return 'standard'
    
    def _extract_operational_limits(self, equipment: Dict) -> Dict:
        """Extract operational limits from equipment specifications."""
        specs = equipment.get('specifications', '')
        
        limits = {
            'temperature_range': None,
            'pressure_range': None,
            'voltage_range': None,
            'current_range': None
        }
        
        # Extract temperature range
        temp_match = re.search(r'(\d+)\s*[°°]\s*[CF]\s*to\s*(\d+)\s*[°°]\s*[CF]', specs, re.IGNORECASE)
        if temp_match:
            limits['temperature_range'] = f"{temp_match.group(1)}° to {temp_match.group(2)}°"
        
        # Extract pressure range
        pressure_match = re.search(r'(\d+)\s*(?:psi|bar|pa|kpa|mpa)\s*to\s*(\d+)\s*(?:psi|bar|pa|kpa|mpa)', specs, re.IGNORECASE)
        if pressure_match:
            limits['pressure_range'] = f"{pressure_match.group(1)} to {pressure_match.group(2)}"
        
        return limits
    
    def _extract_replacement_schedule(self, equipment: Dict) -> str:
        """Extract replacement schedule from equipment specifications."""
        specs = equipment.get('specifications', '')
        maintenance = equipment.get('maintenance_requirements', '')
        
        schedule_patterns = [
            r'(\d+)\s*(?:hours?|hrs?)\s*(?:or\s*)?(?:every\s*)?(\d+)\s*(?:months?|years?)',
            r'replace\s*(?:every\s*)?(\d+)\s*(?:hours?|hrs?|months?|years?)',
        ]
        
        for pattern in schedule_patterns:
            match = re.search(pattern, specs + ' ' + maintenance, re.IGNORECASE)
            if match:
                return f"Replace every {match.group(1)} hours"
        
        return 'standard_schedule'
    
    def _structure_processing_stages(self, stages: List[Any]) -> List[Dict]:
        """Structure processing stage information."""
        structured_stages = []
        
        for stage in stages:
            if hasattr(stage, 'stage'):
                structured_stages.append({
                    'stage': stage.stage.value if hasattr(stage.stage, 'value') else str(stage.stage),
                    'success': stage.success,
                    'confidence': stage.confidence,
                    'errors': stage.errors
                })
        
        return structured_stages
    
    def _extract_quality_metrics(self, results: Dict) -> Dict:
        """Extract quality metrics from results."""
        return {
            'text_quality': results.get('quality_metrics', {}),
            'extraction_confidence': results.get('document_info', {}).get('confidence_score', 0.0),
            'processing_success': len(results.get('errors', [])) == 0
        }
    
    def _calculate_overall_confidence(self, results: Dict) -> float:
        """Calculate overall confidence score."""
        stages = results.get('processing_stages', [])
        if not stages:
            return 0.0
        
        confidences = [stage.confidence for stage in stages if hasattr(stage, 'confidence')]
        return sum(confidences) / len(confidences) if confidences else 0.0
