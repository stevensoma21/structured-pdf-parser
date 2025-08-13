# ML Core - High-Performance Extraction Engine

A high-performance, Rust-based extraction engine for processing technical documentation.

## Features

- Fast Extraction: Native Rust implementation
- Modular Design: Clean separation of concerns
- Python Integration: Seamless Python bindings
- Configuration Management: Flexible configuration system

## Quick Start

```bash
# Build Rust library
cargo build --release

# Use in Python
import ml_core
ml_core.initialize_engine("config/license.json")
```

## Architecture

```
core/
├── engine/          # Core extraction engine
├── security/        # Configuration validation
├── licensing/       # License management
└── src/            # Main library entry point
```
