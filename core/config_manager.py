#!/usr/bin/env python3
"""
Configuration Manager for ML Core
Handles configuration loading, validation, and feature access control.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class ConfigManager:
    """Configuration manager for the ML pipeline."""
    
    def __init__(self, config_path: str = "config/license.json"):
        self.config_path = config_path
        self.config = {}
        self.features = []
        self.expires_at = None
        
    def load_config(self) -> bool:
        """Load configuration from file."""
        try:
            if not os.path.exists(self.config_path):
                print(f"Config not found: {self.config_path}")
                return False
                
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                
            # Validate configuration
            if self._validate_config():
                self.features = self.config.get('features', [])
                self.expires_at = datetime.fromisoformat(self.config['expires_at'].replace('Z', '+00:00'))
                print("Configuration loaded successfully")
                return True
            else:
                print("Configuration validation failed")
                return False
                
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """Validate configuration structure."""
        required_fields = ['customer_id', 'features', 'expires_at']
        return all(field in self.config for field in required_fields)
    
    def is_valid(self) -> bool:
        """Check if configuration is still valid."""
        if not self.expires_at:
            return False
        return datetime.now(self.expires_at.tzinfo) < self.expires_at
    
    def has_feature(self, feature: str) -> bool:
        """Check if a feature is available."""
        return feature in self.features
    
    def get_customer_id(self) -> str:
        """Get customer ID from config."""
        return self.config.get('customer_id', 'unknown')
    
    def get_available_features(self) -> List[str]:
        """Get list of available features."""
        return self.features.copy()
    
    def days_remaining(self) -> int:
        """Get days remaining until expiration."""
        if not self.expires_at:
            return 0
        delta = self.expires_at - datetime.now(self.expires_at.tzinfo)
        return max(0, delta.days)

class FeatureAccess:
    """Feature access control."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def check_access(self, feature: str) -> bool:
        """Check if user has access to a feature."""
        return (self.config_manager.is_valid() and 
                self.config_manager.has_feature(feature))
    
    def get_available_features(self) -> List[str]:
        """Get list of available features."""
        if self.config_manager.is_valid():
            return self.config_manager.get_available_features()
        return []

def create_demo_config(customer_id: str = "demo_user", days: int = 14) -> Dict:
    """Create a demo configuration."""
    expires_at = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"
    
    return {
        "customer_id": customer_id,
        "features": [
            "module_extraction",
            "step_extraction", 
            "flow_extraction",
            "llm_integration"
        ],
        "expires_at": expires_at,
        "metadata": {
            "created_at": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0"
        }
    }

def save_config(config: Dict, output_path: str) -> bool:
    """Save configuration to file."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Config saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def main():
    """Demo configuration management."""
    print("Configuration Manager Demo")
    print("=" * 40)
    
    # Create demo config
    config = create_demo_config("demo_customer", 30)
    
    # Save config
    config_path = "config/demo_license.json"
    if save_config(config, config_path):
        # Load and validate
        manager = ConfigManager(config_path)
        if manager.load_config():
            print(f"Customer ID: {manager.get_customer_id()}")
            print(f"Features: {', '.join(manager.get_available_features())}")
            print(f"Days remaining: {manager.days_remaining()}")
            print(f"Valid: {manager.is_valid()}")
            
            # Test feature access
            access = FeatureAccess(manager)
            print(f"Module extraction: {access.check_access('module_extraction')}")
            print(f"Advanced features: {access.check_access('advanced_features')}")

if __name__ == "__main__":
    main()
