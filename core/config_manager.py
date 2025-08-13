#!/usr/bin/env python3
"""
Configuration Manager for ML Core
Handles configuration loading, validation, and feature access control.
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Hardcoded security constants - must match Rust implementation
BUILD_TIMESTAMP = 1734123456  # Must match Rust BUILD_TIMESTAMP (December 13, 2024)
HARDCODED_EXPIRATION_DAYS = 14  # Must match Rust HARDCODED_EXPIRATION_DAYS
SECURITY_SALT = "ml_core_2024_secure"  # Must match Rust SECURITY_SALT

class ConfigManager:
    """Configuration manager for the ML pipeline with secure validation."""
    
    def __init__(self, config_path: str = "config/license.json"):
        self.config_path = config_path
        self.config = {}
        self.features = []
        self.expires_at = None
        self.build_signature = None
        
    def load_config(self) -> bool:
        """Load configuration from file with secure validation."""
        try:
            if not os.path.exists(self.config_path):
                print(f"Config not found: {self.config_path}")
                return False
                
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                
            # Multi-layer validation
            if self._validate_config_secure():
                self.features = self.config.get('features', [])
                self.expires_at = datetime.fromisoformat(self.config['expires_at'].replace('Z', '+00:00'))
                self.build_signature = self.config.get('build_signature', '')
                print("Configuration loaded and validated successfully")
                return True
            else:
                print("Configuration validation failed")
                return False
                
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def _validate_config_secure(self) -> bool:
        """Validate configuration with multiple security layers."""
        # Layer 1: Required fields check
        required_fields = ['customer_id', 'features', 'expires_at', 'build_signature']
        if not all(field in self.config for field in required_fields):
            return False
        
        # Layer 2: Hardcoded expiration validation
        if not self._validate_hardcoded_expiration():
            return False
        
        # Layer 3: Security signature validation
        if not self._validate_security_signature():
            return False
        
        # Layer 4: Build timestamp validation
        if not self._validate_build_timestamp():
            return False
        
        return True
    
    def _validate_hardcoded_expiration(self) -> bool:
        """Validate against hardcoded expiration."""
        # Calculate expected expiration from hardcoded build timestamp
        build_date = datetime.fromtimestamp(BUILD_TIMESTAMP)
        expected_expiration = build_date + timedelta(days=HARDCODED_EXPIRATION_DAYS)
        
        # Parse config expiration and make timezone-aware
        config_expiration_str = self.config['expires_at'].replace('Z', '+00:00')
        config_expiration = datetime.fromisoformat(config_expiration_str)
        
        # Make expected expiration timezone-aware for comparison
        expected_expiration = expected_expiration.replace(tzinfo=config_expiration.tzinfo)
        
        # Config expiration must match hardcoded expiration
        return abs((config_expiration - expected_expiration).total_seconds()) < 3600  # 1 hour tolerance
    
    def _validate_security_signature(self) -> bool:
        """Validate security signature."""
        customer_id = self.config.get('customer_id', '')
        build_date = datetime.fromtimestamp(BUILD_TIMESTAMP)
        
        # Generate expected signature
        expected_signature = self._generate_security_signature(customer_id, build_date)
        actual_signature = self.config.get('build_signature', '')
        
        return expected_signature == actual_signature
    
    def _validate_build_timestamp(self) -> bool:
        """Validate build timestamp."""
        build_date = datetime.fromtimestamp(BUILD_TIMESTAMP)
        current_time = datetime.now()
        
        # Build date should not be in the future
        return build_date <= current_time
    
    def _generate_security_signature(self, customer_id: str, build_date: datetime) -> str:
        """Generate security signature matching Rust implementation."""
        # Create signature data
        signature_data = f"{customer_id}:{int(build_date.timestamp())}:{SECURITY_SALT}"
        
        # Generate hash
        return hashlib.sha256(signature_data.encode()).hexdigest()[:16]
    
    def is_valid(self) -> bool:
        """Check if configuration is still valid with secure validation."""
        if not self.expires_at:
            return False
        
        # Check against hardcoded expiration
        build_date = datetime.fromtimestamp(BUILD_TIMESTAMP)
        hardcoded_expiration = build_date + timedelta(days=HARDCODED_EXPIRATION_DAYS)
        
        # Make timezone-aware for comparison
        current_time = datetime.now().replace(tzinfo=self.expires_at.tzinfo)
        hardcoded_expiration = hardcoded_expiration.replace(tzinfo=self.expires_at.tzinfo)
        
        return current_time < hardcoded_expiration
    
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
        """Get days remaining until hardcoded expiration."""
        build_date = datetime.fromtimestamp(BUILD_TIMESTAMP)
        hardcoded_expiration = build_date + timedelta(days=HARDCODED_EXPIRATION_DAYS)
        current_time = datetime.now()
        
        # Make timezone-aware for comparison
        if self.expires_at:
            current_time = current_time.replace(tzinfo=self.expires_at.tzinfo)
            hardcoded_expiration = hardcoded_expiration.replace(tzinfo=self.expires_at.tzinfo)
        
        if current_time < hardcoded_expiration:
            delta = hardcoded_expiration - current_time
            return max(0, delta.days)
        else:
            return 0
    
    def get_security_info(self) -> Dict[str, str]:
        """Get security information."""
        build_date = datetime.fromtimestamp(BUILD_TIMESTAMP)
        hardcoded_expiration = build_date + timedelta(days=HARDCODED_EXPIRATION_DAYS)
        
        return {
            "build_timestamp": str(BUILD_TIMESTAMP),
            "hardcoded_expiration_days": str(HARDCODED_EXPIRATION_DAYS),
            "build_date": build_date.isoformat(),
            "expiration_date": hardcoded_expiration.isoformat(),
            "days_remaining": str(self.days_remaining()),
            "security_level": "Maximum",
            "signature_valid": str(self._validate_security_signature())
        }

class FeatureAccess:
    """Feature access control with secure validation."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.access_count = 0
    
    def check_access(self, feature: str) -> bool:
        """Check if user has access to a feature with security validation."""
        # Increment access counter
        self.access_count += 1
        
        # Check access limits
        if self.access_count > 1000:
            return False  # Too many access attempts
        
        # Multi-layer validation
        config_valid = self.config_manager.is_valid()
        feature_available = self.config_manager.has_feature(feature)
        signature_valid = self.config_manager._validate_security_signature()
        
        return config_valid and feature_available and signature_valid
    
    def get_available_features(self) -> List[str]:
        """Get list of available features."""
        if self.config_manager.is_valid():
            return self.config_manager.get_available_features()
        return []
    
    def get_security_status(self) -> Dict[str, str]:
        """Get comprehensive security status."""
        status = self.config_manager.get_security_info()
        status["access_attempts"] = str(self.access_count)
        status["config_valid"] = str(self.config_manager.is_valid())
        return status

def create_secure_config(customer_id: str = "demo_user") -> Dict:
    """Create a secure configuration with hardcoded expiration."""
    # Calculate expiration from hardcoded build timestamp
    build_date = datetime.fromtimestamp(BUILD_TIMESTAMP)
    expiration = build_date + timedelta(days=HARDCODED_EXPIRATION_DAYS)
    
    # Generate security signature
    signature_data = f"{customer_id}:{int(build_date.timestamp())}:{SECURITY_SALT}"
    signature = hashlib.sha256(signature_data.encode()).hexdigest()[:16]
    
    return {
        "customer_id": customer_id,
        "features": [
            "module_extraction",
            "step_extraction", 
            "flow_extraction",
            "llm_integration"
        ],
        "expires_at": expiration.isoformat() + "Z",
        "build_signature": signature,
        "metadata": {
            "created_at": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "security_level": "Maximum"
        }
    }

def save_config(config: Dict, output_path: str) -> bool:
    """Save configuration to file."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Secure config saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def main():
    """Demo secure configuration management."""
    print("Secure Configuration Manager Demo")
    print("=" * 50)
    
    # Create secure config
    config = create_secure_config("secure_customer")
    
    # Save config
    config_path = "config/secure_license.json"
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
            
            # Show security info
            print(f"\nSecurity Information:")
            security_info = access.get_security_status()
            for key, value in security_info.items():
                print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
