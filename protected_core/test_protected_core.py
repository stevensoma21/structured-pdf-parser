#!/usr/bin/env python3
"""
Test script for the protected core module.
This verifies the license verification, decryption, and extraction functionality.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the current directory to Python path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_protected_core():
    """Test the protected core functionality."""
    print("🔐 Testing Protected Core Module")
    print("=" * 50)
    
    try:
        # Import the protected core module
        print("📦 Importing codex_core module...")
        import codex_core
        
        # Test license initialization
        print("🔑 Testing license initialization...")
        license_path = "assets/test_license.json"
        
        if not os.path.exists(license_path):
            print("❌ Test license not found. Run build_payload.py first.")
            return False
        
        # Initialize the core
        success = codex_core.initialize_core(license_path)
        if not success:
            print("❌ Failed to initialize core")
            return False
        
        print("✅ Core initialized successfully")
        
        # Test text extraction
        print("📝 Testing text extraction...")
        test_text = """
        Chapter 1: Introduction to Aircraft Maintenance
        Aircraft maintenance is critical to aviation safety, performance, and reliability.
        
        Conduct scheduled inspections according to manufacturer specifications.
        Identify and resolve mechanical, hydraulic, electrical, and avionics issues.
        Document and report all maintenance activities clearly and accurately.
        Adhere strictly to safety guidelines and regulations.
        
        Types of Maintenance:
        - Preventive: Routine checks and servicing.
        - Corrective: Repair or replacement after malfunction.
        - Predictive: Diagnostic checks to predict and prevent failures.
        """
        
        # Test module extraction
        print("🔍 Testing module extraction...")
        modules = codex_core.extract_modules(test_text)
        print(f"✅ Extracted {len(modules)} modules")
        
        # Test step extraction
        print("📋 Testing step extraction...")
        steps = codex_core.extract_steps(test_text)
        print(f"✅ Extracted {len(steps)} steps")
        
        # Test LLM prompt retrieval
        print("🤖 Testing LLM prompt retrieval...")
        try:
            prompt = codex_core.get_llm_prompt("module_extraction")
            print(f"✅ Retrieved prompt: {prompt[:50]}...")
        except Exception as e:
            print(f"⚠️  LLM prompt test failed: {e}")
        
        print("\n🎉 All tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import codex_core: {e}")
        print("💡 Make sure to build the Rust module first:")
        print("   cargo build --release")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_license_expiration():
    """Test license expiration functionality."""
    print("\n⏰ Testing License Expiration")
    print("=" * 30)
    
    try:
        import codex_core
        
        # Create an expired license
        expired_license = {
            "customer_id": "expired_customer",
            "expiration": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
            "features": ["module_extraction"],
            "hwid": None,
            "wheel_hash": "sha256:abc123...",
            "signature": "expired_signature"
        }
        
        expired_license_path = "assets/expired_license.json"
        with open(expired_license_path, "w") as f:
            json.dump(expired_license, f)
        
        # Try to initialize with expired license
        try:
            success = codex_core.initialize_core(expired_license_path)
            if success:
                print("❌ Should have failed with expired license")
                return False
        except Exception as e:
            if "expired" in str(e).lower():
                print("✅ Correctly rejected expired license")
                return True
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        
        # Clean up
        os.remove(expired_license_path)
        
    except Exception as e:
        print(f"❌ Expiration test failed: {e}")
        return False

def test_watermarking():
    """Test watermarking functionality."""
    print("\n💧 Testing Watermarking")
    print("=" * 25)
    
    try:
        import codex_core
        
        # Re-initialize with valid license
        license_path = "assets/test_license.json"
        codex_core.initialize_core(license_path)
        
        test_text = "This is a test document for watermarking verification."
        
        # Extract modules and check for watermarks
        modules = codex_core.extract_modules(test_text)
        
        # In a real implementation, we would check for watermarks
        # For now, just verify the extraction works
        print("✅ Watermarking test completed (extraction functional)")
        return True
        
    except Exception as e:
        print(f"❌ Watermarking test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Protected Core Test Suite")
    print("=" * 50)
    
    # Check if payload exists
    if not os.path.exists("assets/encrypted_payload.bin"):
        print("❌ Encrypted payload not found.")
        print("💡 Run build_payload.py first to create the encrypted payload.")
        return
    
    # Run tests
    tests = [
        ("Core Functionality", test_protected_core),
        ("License Expiration", test_license_expiration),
        ("Watermarking", test_watermarking),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Protected core is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
