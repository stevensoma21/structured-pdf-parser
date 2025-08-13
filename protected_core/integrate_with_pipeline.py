#!/usr/bin/env python3
"""
Integration script to use the protected core with the existing ML pipeline.
This replaces the rule-based extraction with the protected core module.
"""

import sys
import os
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_protected_pipeline():
    """Create a protected version of the pipeline that uses the encrypted core."""
    
    protected_pipeline_code = '''
#!/usr/bin/env python3
"""
Protected ML Pipeline - Uses encrypted core for extraction logic.
This version integrates the protected core module for IP protection.
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime

# Import the protected core
try:
    import codex_core
    PROTECTED_CORE_AVAILABLE = True
except ImportError:
    print("⚠️  Protected core not available, falling back to rule-based extraction")
    PROTECTED_CORE_AVAILABLE = False

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using existing methods."""
    import fitz  # PyMuPDF
    
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def initialize_protected_core(license_path="protected_core/assets/test_license.json"):
    """Initialize the protected core with license verification."""
    if not PROTECTED_CORE_AVAILABLE:
        print("❌ Protected core not available")
        return False
    
    try:
        success = codex_core.initialize_core(license_path)
        if success:
            print("✅ Protected core initialized successfully")
            return True
        else:
            print("❌ Failed to initialize protected core")
            return False
    except Exception as e:
        print(f"❌ Protected core initialization error: {e}")
        return False

def extract_protected_modules(text):
    """Extract modules using the protected core."""
    if not PROTECTED_CORE_AVAILABLE:
        return extract_fallback_modules(text)
    
    try:
        modules = codex_core.extract_modules(text)
        return modules
    except Exception as e:
        print(f"⚠️  Protected module extraction failed: {e}")
        return extract_fallback_modules(text)

def extract_protected_steps(text):
    """Extract steps using the protected core."""
    if not PROTECTED_CORE_AVAILABLE:
        return extract_fallback_steps(text)
    
    try:
        steps = codex_core.extract_steps(text)
        return steps
    except Exception as e:
        print(f"⚠️  Protected step extraction failed: {e}")
        return extract_fallback_steps(text)

def get_protected_llm_prompt(prompt_type):
    """Get LLM prompt from protected core."""
    if not PROTECTED_CORE_AVAILABLE:
        return get_fallback_prompt(prompt_type)
    
    try:
        return codex_core.get_llm_prompt(prompt_type)
    except Exception as e:
        print(f"⚠️  Protected prompt retrieval failed: {e}")
        return get_fallback_prompt(prompt_type)

def extract_fallback_modules(text):
    """Fallback module extraction using basic patterns."""
    modules = []
    
    # Basic chapter detection
    chapter_match = re.search(r'Chapter \\d+:\\s*([^.!?]+)', text)
    if chapter_match:
        modules.append({
            "module_id": "mod_intro",
            "heading": chapter_match.group(0),
            "summary": "Extracted using fallback patterns",
            "steps": [],
            "source": "fallback",
            "confidence": 0.7
        })
    
    return modules

def extract_fallback_steps(text):
    """Fallback step extraction using basic patterns."""
    steps = []
    
    # Basic step patterns
    step_patterns = [
        r'Conduct scheduled inspections[^.!?]*[.!?]',
        r'Identify and resolve[^.!?]*[.!?]',
        r'Document and report[^.!?]*[.!?]',
        r'Adhere strictly to[^.!?]*[.!?]',
    ]
    
    for i, pattern in enumerate(step_patterns):
        if re.search(pattern, text):
            steps.append({
                "step_id": f"s-{i+1:03d}",
                "text": re.search(pattern, text).group(0),
                "category": "general",
                "source": "fallback",
                "confidence": 0.7
            })
    
    return steps

def get_fallback_prompt(prompt_type):
    """Fallback LLM prompts."""
    fallback_prompts = {
        "module_extraction": "Extract modules from the text.",
        "step_extraction": "Extract procedural steps from the text.",
        "flow_extraction": "Extract decision flows from the text.",
    }
    return fallback_prompts.get(prompt_type, "Process the text.")

def create_protected_structured_output(pdf_path):
    """Create structured output using protected core."""
    print(f"🔐 Processing with protected core: {pdf_path}")
    
    # Initialize protected core
    if not initialize_protected_core():
        print("⚠️  Using fallback extraction methods")
    
    # Extract text
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None
    
    # Extract using protected core
    modules = extract_protected_modules(text)
    steps = extract_protected_steps(text)
    
    # Create structured output
    doc_id = Path(pdf_path).stem
    title = "Protected Core Extraction"
    
    # Try to extract title from text
    title_match = re.search(r'Chapter \\d+:\\s*([^.!?]+)', text)
    if title_match:
        title = title_match.group(0)
    
    output = {
        "doc_id": doc_id,
        "title": title,
        "modules": modules,
        "flows": [],
        "metadata": {
            "extraction_mode": "protected_core" if PROTECTED_CORE_AVAILABLE else "fallback",
            "schema_version": "1.0.0",
            "protection_level": "encrypted" if PROTECTED_CORE_AVAILABLE else "basic",
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    return output

def process_pdf_with_protection(pdf_path, output_dir="results"):
    """Process a PDF file using the protected pipeline."""
    os.makedirs(output_dir, exist_ok=True)
    
    output = create_protected_structured_output(pdf_path)
    if not output:
        return None
    
    # Save output
    output_file = Path(output_dir) / f"{Path(pdf_path).stem}_protected_output.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Protected output saved to: {output_file}")
    return output_file

def main():
    """Main function for protected pipeline."""
    if len(sys.argv) < 2:
        print("Usage: python protected_pipeline.py <pdf_file>")
        return
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    # Process with protection
    output_file = process_pdf_with_protection(pdf_path)
    if output_file:
        print(f"🎉 Protected processing complete: {output_file}")
    else:
        print("❌ Protected processing failed")

if __name__ == "__main__":
    main()
'''
    
    # Write the protected pipeline
    protected_file = "protected_pipeline.py"
    with open(protected_file, "w") as f:
        f.write(protected_pipeline_code)
    
    print(f"✅ Created protected pipeline: {protected_file}")
    return protected_file

def create_license_generator():
    """Create a license generator for customers."""
    
    license_generator_code = '''
#!/usr/bin/env python3
"""
License Generator for Protected Core
This generates customer licenses with expiration dates.
"""

import json
import hashlib
import uuid
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

class LicenseGenerator:
    def __init__(self, private_key_path="license_keys/private_key.pem"):
        self.private_key_path = private_key_path
        self.load_or_generate_key()
    
    def load_or_generate_key(self):
        """Load existing private key or generate a new one."""
        try:
            with open(self.private_key_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(), password=None
                )
            print("✅ Loaded existing private key")
        except FileNotFoundError:
            print("🔑 Generating new private key...")
            self.private_key = ed25519.Ed25519PrivateKey.generate()
            
            # Save private key
            os.makedirs(os.path.dirname(self.private_key_path), exist_ok=True)
            with open(self.private_key_path, "wb") as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            print("✅ Generated and saved new private key")
    
    def generate_license(self, customer_id, expiration_days=14, features=None):
        """Generate a license for a customer."""
        if features is None:
            features = ["module_extraction", "step_extraction", "flow_extraction", "llm_integration"]
        
        expiration = datetime.utcnow() + timedelta(days=expiration_days)
        
        # Create license data
        license_data = {
            "customer_id": customer_id,
            "expiration": expiration.isoformat() + "Z",
            "features": features,
            "hwid": None,  # Optional hardware ID
            "wheel_hash": "sha256:abc123...",  # Wheel hash for verification
            "license_id": str(uuid.uuid4()),
            "issued_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Create signature
        data_to_sign = f"{customer_id}:{license_data['expiration']}:{license_data['wheel_hash']}"
        signature = self.private_key.sign(data_to_sign.encode())
        license_data["signature"] = signature.hex()
        
        return license_data
    
    def save_license(self, license_data, output_path):
        """Save license to file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(license_data, f, indent=2)
        print(f"✅ License saved to: {output_path}")

def main():
    """Main function for license generation."""
    import os
    
    generator = LicenseGenerator()
    
    # Generate sample licenses
    licenses = [
        ("customer_001", 14, ["module_extraction", "step_extraction"]),
        ("customer_002", 30, ["module_extraction", "step_extraction", "flow_extraction"]),
        ("customer_003", 90, ["module_extraction", "step_extraction", "flow_extraction", "llm_integration"]),
    ]
    
    for customer_id, days, features in licenses:
        license_data = generator.generate_license(customer_id, days, features)
        output_path = f"licenses/{customer_id}_license.json"
        generator.save_license(license_data, output_path)
        
        print(f"📄 Generated license for {customer_id}:")
        print(f"   Expires: {license_data['expiration']}")
        print(f"   Features: {', '.join(features)}")
        print(f"   License ID: {license_data['license_id']}")
        print()

if __name__ == "__main__":
    main()
'''
    
    # Write the license generator
    license_file = "license_generator.py"
    with open(license_file, "w") as f:
        f.write(license_generator_code)
    
    print(f"✅ Created license generator: {license_file}")
    return license_file

def main():
    """Main integration function."""
    print("🔐 Protected Core Integration")
    print("=" * 40)
    
    # Create protected pipeline
    pipeline_file = create_protected_pipeline()
    
    # Create license generator
    license_file = create_license_generator()
    
    print(f"\n🎉 Integration complete!")
    print("=" * 40)
    print("📁 Generated files:")
    print(f"   • {pipeline_file} - Protected pipeline using encrypted core")
    print(f"   • {license_file} - License generator for customers")
    print("\n🔧 Usage:")
    print("   1. Build protected core: cd protected_core && cargo build --release")
    print("   2. Generate test payload: python build_payload.py")
    print("   3. Test protected core: python test_protected_core.py")
    print("   4. Run protected pipeline: python protected_pipeline.py <pdf_file>")
    print("   5. Generate licenses: python license_generator.py")

if __name__ == "__main__":
    main()
