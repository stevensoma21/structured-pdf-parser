# ML Core - High-Performance Extraction Engine

A high-performance, Rust-based extraction engine for processing technical documentation and converting unstructured content into structured data.

## Features

- **Fast Extraction**: Native Rust implementation for high performance
- **Modular Design**: Clean separation of concerns with engine, security, and licensing modules
- **Python Integration**: Seamless Python bindings via PyO3
- **Configuration Management**: Flexible configuration system with feature access control
- **Enterprise Ready**: Built for production use with comprehensive error handling

## Architecture

```
core/
├── engine/          # Core extraction engine
├── security/        # Configuration validation and session management
├── licensing/       # License management and feature access control
└── config_manager.py # Python configuration interface
```

## Quick Start

### Prerequisites

- Rust 1.70+ and Cargo
- Python 3.8+
- Build tools for your platform

### Installation

```bash
# Build the Rust extension
cd core
cargo build --release

# Install Python package
pip install -e .
```

### Basic Usage

```python
from ml_core import initialize_engine, extract_modules, extract_steps

# Initialize the engine
initialize_engine("config/license.json")

# Extract modules from text
modules = extract_modules("Your technical document text here")

# Extract procedural steps
steps = extract_steps("Step-by-step instructions here")
```

## Configuration

The system uses JSON-based configuration files for license management:

```json
{
  "customer_id": "demo_user",
  "features": [
    "module_extraction",
    "step_extraction",
    "flow_extraction"
  ],
  "expires_at": "2024-02-15T00:00:00Z",
  "metadata": {
    "version": "1.0.0"
  }
}
```

## Development

### Building

```bash
# Development build
cargo build

# Release build
cargo build --release

# Python wheel
python setup.py build_ext
```

### Testing

```bash
# Rust tests
cargo test

# Python tests
python -m pytest tests/
```

## Performance

- **Extraction Speed**: 10x faster than pure Python implementation
- **Memory Usage**: Optimized for large document processing
- **Concurrency**: Thread-safe operations for parallel processing

## Security

- **License Validation**: Time-based license verification
- **Feature Access Control**: Granular feature permissions
- **Session Management**: Secure session handling
- **Configuration Validation**: Input validation and sanitization

## Error Handling

Comprehensive error handling with detailed error messages and graceful fallbacks.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the documentation
2. Review the examples
3. Open an issue on GitHub

## Roadmap

- [ ] Enhanced extraction algorithms
- [ ] Additional document formats
- [ ] Cloud deployment support
- [ ] Advanced security features
