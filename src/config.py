"""
Configuration Module

Handles loading and validation of configuration files.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict:
    """
    Load configuration from file or use defaults.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config = get_default_config()
    
    if config_path:
        config_path = Path(config_path)
        if config_path.exists():
            try:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    with open(config_path, 'r') as f:
                        file_config = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    with open(config_path, 'r') as f:
                        file_config = json.load(f)
                else:
                    logger.warning(f"Unsupported config file format: {config_path.suffix}")
                    return config
                
                # Merge configurations
                config = merge_configs(config, file_config)
                logger.info(f"Loaded configuration from: {config_path}")
                
            except Exception as e:
                logger.error(f"Error loading configuration from {config_path}: {e}")
        else:
            logger.warning(f"Configuration file not found: {config_path}")
    
    # Load from environment variables
    config = load_from_env(config)
    
    return config


def get_default_config() -> Dict:
    """Get default configuration."""
    return {
        'log_level': 'INFO',
        'confidence_thresholds': {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        },
        'pdf_processor': {
            'ocr_enabled': True,
            'min_confidence': 0.7,
            'extraction_methods': ['pymupdf', 'pdfplumber', 'ocr']
        },
        'nlp_processor': {
            'spacy_model': 'en_core_web_sm',
            'sentence_transformer_model': 'all-MiniLM-L6-v2',
            'enable_dependency_parsing': True,
            'enable_semantic_search': True
        },
        'llm_processor': {
            'model_name': 'gpt2',
            'max_length': 512,
            'temperature': 0.7,
            'use_ctransformers': True,
            'enable_llm': True
        },
        'agentic_workflow': {
            'enable_quality_assessment': True,
            'enable_fallback_strategies': True,
            'max_processing_time': 300  # 5 minutes
        },
        'data_structurer': {
            'output_format': 'json',
            'include_metadata': True,
            'include_raw_data': False
        },
        'security': {
            'encrypt_output': False,
            'access_control': False,
            'audit_logging': True
        },
        'performance': {
            'max_memory_usage': '4GB',
            'batch_size': 1,
            'parallel_processing': False
        }
    }


def merge_configs(base_config: Dict, override_config: Dict) -> Dict:
    """Merge two configuration dictionaries."""
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged


def load_from_env(config: Dict) -> Dict:
    """Load configuration from environment variables."""
    env_mappings = {
        'LOG_LEVEL': ('log_level', str),
        'LLM_MODEL_NAME': ('llm_processor.model_name', str),
        'LLM_MAX_LENGTH': ('llm_processor.max_length', int),
        'LLM_TEMPERATURE': ('llm_processor.temperature', float),
        'PDF_OCR_ENABLED': ('pdf_processor.ocr_enabled', bool),
        'NLP_SPACY_MODEL': ('nlp_processor.spacy_model', str),
        'ENABLE_LLM': ('llm_processor.enable_llm', bool),
        'MAX_MEMORY_USAGE': ('performance.max_memory_usage', str),
        'BATCH_SIZE': ('performance.batch_size', int),
        'ENCRYPT_OUTPUT': ('security.encrypt_output', bool),
        'AUDIT_LOGGING': ('security.audit_logging', bool)
    }
    
    for env_var, (config_path, value_type) in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            try:
                if value_type == bool:
                    parsed_value = env_value.lower() in ['true', '1', 'yes', 'on']
                else:
                    parsed_value = value_type(env_value)
                
                set_nested_value(config, config_path, parsed_value)
                logger.debug(f"Loaded {config_path} from environment variable {env_var}")
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid value for environment variable {env_var}: {env_value}")
    
    return config


def set_nested_value(config: Dict, path: str, value):
    """Set a nested value in configuration dictionary."""
    keys = path.split('.')
    current = config
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def validate_config(config: Dict) -> Dict:
    """
    Validate configuration and return validation results.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Validation results
    """
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check required sections
    required_sections = ['pdf_processor', 'nlp_processor', 'llm_processor']
    for section in required_sections:
        if section not in config:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Missing required configuration section: {section}")
    
    # Validate confidence thresholds
    if 'confidence_thresholds' in config:
        thresholds = config['confidence_thresholds']
        for level, threshold in thresholds.items():
            if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
                validation_results['valid'] = False
                validation_results['errors'].append(f"Invalid confidence threshold for {level}: {threshold}")
    
    # Validate LLM configuration
    if 'llm_processor' in config:
        llm_config = config['llm_processor']
        if 'max_length' in llm_config and (not isinstance(llm_config['max_length'], int) or llm_config['max_length'] <= 0):
            validation_results['valid'] = False
            validation_results['errors'].append("LLM max_length must be a positive integer")
        
        if 'temperature' in llm_config and (not isinstance(llm_config['temperature'], (int, float)) or llm_config['temperature'] < 0 or llm_config['temperature'] > 2):
            validation_results['valid'] = False
            validation_results['errors'].append("LLM temperature must be between 0 and 2")
    
    # Validate performance configuration
    if 'performance' in config:
        perf_config = config['performance']
        if 'batch_size' in perf_config and (not isinstance(perf_config['batch_size'], int) or perf_config['batch_size'] <= 0):
            validation_results['valid'] = False
            validation_results['errors'].append("Batch size must be a positive integer")
    
    # Check for deprecated or unknown keys
    known_keys = {
        'log_level', 'confidence_thresholds', 'pdf_processor', 'nlp_processor',
        'llm_processor', 'agentic_workflow', 'data_structurer', 'security', 'performance'
    }
    
    for key in config.keys():
        if key not in known_keys:
            validation_results['warnings'].append(f"Unknown configuration key: {key}")
    
    return validation_results


def save_config(config: Dict, output_path: str):
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        output_path: Output file path
    """
    output_path = Path(output_path)
    
    try:
        if output_path.suffix.lower() in ['.yaml', '.yml']:
            with open(output_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        elif output_path.suffix.lower() == '.json':
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
        else:
            raise ValueError(f"Unsupported output format: {output_path.suffix}")
        
        logger.info(f"Configuration saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving configuration to {output_path}: {e}")
        raise
