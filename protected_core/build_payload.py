#!/usr/bin/env python3
"""
Build and encrypt the extraction rules payload for the protected core.
This script creates the encrypted binary blob that contains all sensitive logic.
"""

import json
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
from datetime import datetime, timedelta

def create_extraction_rules():
    """Create the extraction rules that will be encrypted."""
    return {
        "module_patterns": [
            r"Chapter \d+:\s*([^.!?]+)",
            r"Section \d+\.\d+:\s*([^.!?]+)",
            r"Module \d+:\s*([^.!?]+)",
            r"^([A-Z][^.!?]+(?:Maintenance|Procedure|Process|System))",
        ],
        "step_patterns": [
            r"Conduct scheduled inspections[^.!?]*[.!?]",
            r"Identify and resolve[^.!?]*[.!?]",
            r"Document and report[^.!?]*[.!?]",
            r"Adhere strictly to[^.!?]*[.!?]",
            r"Perform \w+ maintenance[^.!?]*[.!?]",
            r"Check \w+ system[^.!?]*[.!?]",
            r"Verify \w+ operation[^.!?]*[.!?]",
            r"Replace \w+ component[^.!?]*[.!?]",
        ],
        "flow_patterns": [
            r"if\s+([^.!?]+)\s+then[^.!?]*[.!?]",
            r"when\s+([^.!?]+)\s+perform[^.!?]*[.!?]",
            r"in case of\s+([^.!?]+)[^.!?]*[.!?]",
        ],
        "taxonomy_patterns": [
            r"(\w+):\s*([^.!?]+)",
            r"(\w+)\s+maintenance:\s*([^.!?]+)",
            r"Type\s+(\w+):\s*([^.!?]+)",
        ],
        "llm_prompts": {
            "module_extraction": """Extract logical modules from the following technical documentation. 
            Look for chapter headings, section titles, and organizational structures.
            Text: {text}
            Return only the module titles and their summaries.""",
            
            "step_extraction": """Identify procedural steps in the following technical documentation.
            Look for action verbs, numbered procedures, and maintenance tasks.
            Text: {text}
            Return only the procedural steps with their categories.""",
            
            "flow_extraction": """Extract decision flows and conditional logic from the following technical documentation.
            Look for if-then statements, decision points, and branching logic.
            Text: {text}
            Return only the decision flows with their conditions and outcomes.""",
            
            "complexity_analysis": """Analyze the complexity of the following technical procedure.
            Consider factors like number of steps, required expertise, time requirements, and safety considerations.
            Text: {text}
            Return a complexity score from 1-10 with justification.""",
        },
        "confidence_thresholds": {
            "module": 0.85,
            "step": 0.90,
            "flow": 0.80,
            "taxonomy": 0.95,
        }
    }

def encrypt_payload(rules_data, master_key):
    """Encrypt the rules payload using AES-GCM."""
    # Convert rules to JSON
    rules_json = json.dumps(rules_data, separators=(',', ':'))
    rules_bytes = rules_json.encode('utf-8')
    
    # Generate a random nonce
    nonce = os.urandom(12)
    
    # Create AES-GCM cipher
    cipher = AESGCM(master_key)
    
    # Encrypt the data
    ciphertext = cipher.encrypt(nonce, rules_bytes, None)
    
    # Combine nonce and ciphertext
    encrypted_payload = nonce + ciphertext
    
    return encrypted_payload

def create_license(customer_id, expiration_days=14):
    """Create a license file for testing."""
    expiration = datetime.utcnow() + timedelta(days=expiration_days)
    
    # Create license data
    license_data = {
        "customer_id": customer_id,
        "expiration": expiration.isoformat() + "Z",
        "features": ["module_extraction", "step_extraction", "flow_extraction", "llm_integration"],
        "hwid": None,  # Optional hardware ID
        "wheel_hash": "sha256:abc123...",  # Wheel hash for verification
    }
    
    # Create signature (simplified - in production use Ed25519)
    data_to_sign = f"{customer_id}:{license_data['expiration']}:{license_data['wheel_hash']}"
    signature = hashlib.sha256(data_to_sign.encode()).hexdigest()
    license_data["signature"] = signature
    
    return license_data

def main():
    """Main build process."""
    print("🔐 Building Protected Core Payload")
    print("=" * 50)
    
    # Create extraction rules
    print("📝 Creating extraction rules...")
    rules = create_extraction_rules()
    
    # Generate master key (in production, this would be securely stored)
    master_key = b"codex_master_key_2024_secure_32bytes!!"
    
    # Encrypt payload
    print("🔒 Encrypting payload...")
    encrypted_payload = encrypt_payload(rules, master_key)
    
    # Save encrypted payload
    payload_path = "assets/encrypted_payload.bin"
    with open(payload_path, "wb") as f:
        f.write(encrypted_payload)
    
    print(f"✅ Encrypted payload saved to: {payload_path}")
    print(f"📊 Payload size: {len(encrypted_payload)} bytes")
    
    # Create test license
    print("📄 Creating test license...")
    license_data = create_license("test_customer_001", expiration_days=14)
    
    license_path = "assets/test_license.json"
    with open(license_path, "w") as f:
        json.dump(license_data, f, indent=2)
    
    print(f"✅ Test license saved to: {license_path}")
    print(f"⏰ Expires: {license_data['expiration']}")
    
    # Create build info
    build_info = {
        "build_timestamp": datetime.utcnow().isoformat(),
        "payload_size": len(encrypted_payload),
        "rules_version": "1.0.0",
        "encryption_method": "AES-GCM-256",
        "master_key_hash": hashlib.sha256(master_key).hexdigest()[:16],
    }
    
    build_path = "assets/build_info.json"
    with open(build_path, "w") as f:
        json.dump(build_info, f, indent=2)
    
    print(f"✅ Build info saved to: {build_path}")
    
    print("\n🎉 Protected core payload build complete!")
    print("=" * 50)
    print("📁 Generated files:")
    print(f"   • {payload_path} - Encrypted extraction rules")
    print(f"   • {license_path} - Test license (expires in 14 days)")
    print(f"   • {build_path} - Build information")
    print("\n🔧 Next steps:")
    print("   1. Build Rust module: cargo build --release")
    print("   2. Test with Python: python test_protected_core.py")
    print("   3. Package as wheel: python setup.py bdist_wheel")

if __name__ == "__main__":
    main()
