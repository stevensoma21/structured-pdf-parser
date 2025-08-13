# 🔐 Protected Core - IP Protection System

This directory contains the protected core implementation for the ML pipeline, providing robust IP protection through encrypted payloads, license verification, and binary compilation.

## 🏗️ Architecture Overview

The protected core system implements a sophisticated IP protection strategy:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Python App    │    │  Protected Core │    │  License File   │
│                 │    │  (Rust Binary)  │    │                 │
│ • PDF Processing│◄──►│ • Encrypted     │◄──►│ • Customer ID   │
│ • NLP Pipeline  │    │   Rules/Prompts │    │ • Expiration    │
│ • Output Format │    │ • License Check │    │ • Features      │
└─────────────────┘    │ • Watermarking  │    │ • Signature     │
                       └─────────────────┘    └─────────────────┘
```

## 🔧 Components

### 1. **Rust Core Module** (`src/lib.rs`)
- **Purpose**: Binary-compiled extraction logic with encrypted payload
- **Protection**: AES-GCM encrypted rules and prompts embedded in binary
- **Features**: License verification, session management, watermarking

### 2. **Payload Builder** (`build_payload.py`)
- **Purpose**: Creates and encrypts the extraction rules payload
- **Output**: Binary blob with embedded AES-GCM encrypted data
- **Security**: Master key derivation and secure encryption

### 3. **License System**
- **Verification**: Ed25519 signature verification
- **Expiration**: Time-based license expiration (default: 14 days)
- **Features**: Granular feature access control
- **Watermarking**: Customer-specific output watermarking

### 4. **Integration Layer** (`integrate_with_pipeline.py`)
- **Purpose**: Seamless integration with existing ML pipeline
- **Fallback**: Graceful degradation to rule-based extraction
- **Error Handling**: Robust error handling and logging

## 🚀 Quick Start

### 1. Build the Protected Core

```bash
# Navigate to protected core directory
cd protected_core

# Build the Rust module
cargo build --release

# Generate encrypted payload
python build_payload.py

# Test the protected core
python test_protected_core.py
```

### 2. Integrate with Pipeline

```bash
# Create protected pipeline integration
python integrate_with_pipeline.py

# Run protected pipeline on a PDF
python protected_pipeline.py data/sample.pdf
```

### 3. Generate Licenses

```bash
# Generate customer licenses
python license_generator.py
```

## 🔒 Security Features

### **Encryption**
- **Algorithm**: AES-GCM-256 for payload encryption
- **Key Derivation**: PBKDF2 with customer-specific salts
- **Nonce Management**: Secure random nonce generation
- **Memory Protection**: Zeroize sensitive data after use

### **License Verification**
- **Signature**: Ed25519 digital signatures
- **Expiration**: Time-based license expiration
- **Features**: Granular feature access control
- **Hardware Binding**: Optional hardware ID binding

### **Binary Protection**
- **Compilation**: Rust compiled to native binary
- **Obfuscation**: Link-time optimization (LTO)
- **Stripping**: Debug symbols removed
- **Packing**: Binary packed with encrypted payload

### **Watermarking**
- **Customer ID**: Unique watermark per customer
- **Output Tracking**: Watermarked outputs for traceability
- **Tamper Detection**: Integrity checks on watermarked data

## 📋 File Structure

```
protected_core/
├── src/
│   └── lib.rs                 # Main Rust module with PyO3 bindings
├── assets/
│   ├── encrypted_payload.bin  # Encrypted extraction rules
│   ├── test_license.json      # Test license file
│   └── build_info.json        # Build information
├── Cargo.toml                 # Rust dependencies and build config
├── setup.py                   # Python wheel build configuration
├── build_payload.py           # Payload encryption script
├── test_protected_core.py     # Test suite for protected core
├── integrate_with_pipeline.py # Integration with main pipeline
├── license_generator.py       # Customer license generator
└── README.md                  # This file
```

## 🔑 License Management

### **License Structure**
```json
{
  "customer_id": "customer_001",
  "expiration": "2024-01-15T00:00:00Z",
  "features": ["module_extraction", "step_extraction"],
  "hwid": null,
  "wheel_hash": "sha256:abc123...",
  "license_id": "uuid-here",
  "issued_at": "2024-01-01T00:00:00Z",
  "signature": "ed25519-signature-here"
}
```

### **License Generation**
```python
from license_generator import LicenseGenerator

generator = LicenseGenerator()
license_data = generator.generate_license(
    customer_id="customer_001",
    expiration_days=14,
    features=["module_extraction", "step_extraction"]
)
```

## 🛡️ Protection Levels

### **Level 1: Basic Protection**
- Python source code obfuscation
- Basic license checking
- Simple expiration dates

### **Level 2: Enhanced Protection** ⭐ **Current Implementation**
- Rust binary compilation
- AES-GCM encrypted payloads
- Ed25519 license signatures
- Customer watermarking
- Hardware ID binding (optional)

### **Level 3: Advanced Protection**
- Anti-debugging techniques
- Code virtualization
- Network-based license verification
- Advanced obfuscation
- Tamper detection

## 🔍 Testing

### **Test Suite**
```bash
# Run comprehensive test suite
python test_protected_core.py

# Test specific components
python -c "import codex_core; print('Core imported successfully')"
```

### **Test Coverage**
- ✅ License verification
- ✅ Payload decryption
- ✅ Module extraction
- ✅ Step extraction
- ✅ LLM prompt retrieval
- ✅ Expiration handling
- ✅ Watermarking
- ✅ Error handling

## 📦 Distribution

### **Wheel Packaging**
```bash
# Build protected wheel
python setup.py bdist_wheel

# Install from wheel
pip install dist/codex_core-0.1.0-cp39-cp39-macosx_10_9_x86_64.whl
```

### **Private Distribution**
- **GitHub Packages**: Private package registry
- **AWS CodeArtifact**: Enterprise package management
- **JFrog Artifactory**: Enterprise artifact management
- **Hash Pinning**: Secure wheel verification

## 🔧 Configuration

### **Build Configuration** (`Cargo.toml`)
```toml
[profile.release]
opt-level = 3          # Maximum optimization
lto = true            # Link-time optimization
codegen-units = 1     # Single codegen unit
panic = "abort"       # Abort on panic
```

### **Python Integration** (`setup.py`)
```python
ext_modules=[
    RustExtension("codex_core", ".")
],
cmdclass={
    "build_ext": RustBuildExt,
},
```

## 🚨 Security Considerations

### **Key Management**
- **Master Key**: Store securely, never in source code
- **Private Keys**: Use hardware security modules (HSM)
- **Key Rotation**: Regular key rotation procedures
- **Access Control**: Limit access to signing keys

### **Deployment Security**
- **Network Security**: Secure license distribution
- **Access Logging**: Monitor license usage
- **Tamper Detection**: Implement integrity checks
- **Update Mechanism**: Secure update procedures

### **Legal Protection**
- **License Terms**: Clear usage terms and conditions
- **Audit Rights**: License compliance monitoring
- **Enforcement**: Legal recourse for violations
- **Documentation**: Comprehensive usage documentation

## 🆘 Troubleshooting

### **Common Issues**

1. **Import Error**: `ModuleNotFoundError: No module named 'codex_core'`
   - **Solution**: Build Rust module with `cargo build --release`

2. **License Expired**: `License expired`
   - **Solution**: Generate new license with `license_generator.py`

3. **Decryption Failed**: `Decryption failed`
   - **Solution**: Verify license signature and customer ID

4. **Build Failed**: Rust compilation errors
   - **Solution**: Install Rust toolchain and dependencies

### **Debug Mode**
```bash
# Enable debug logging
export CODEX_DEBUG=1
python test_protected_core.py
```

## 📞 Support

For technical support and licensing inquiries:
- **Email**: support@codex.ai
- **Documentation**: [Protected Core Docs](https://docs.codex.ai/protected-core)
- **Issues**: [GitHub Issues](https://github.com/stevensoma21/structured-pdf-parser/issues)

## 📄 License

This protected core system is proprietary software. Unauthorized copying, distribution, or reverse engineering is prohibited.

---

**🔐 Secure • 🚀 Fast • 🛡️ Protected**
