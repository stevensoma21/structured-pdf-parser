#!/usr/bin/env python3
"""
Setup script for the protected core wheel.
This creates a private wheel with the Rust extension module.
"""

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import subprocess
import sys
import os
from pathlib import Path

class RustExtension(Extension):
    def __init__(self, name, path):
        Extension.__init__(self, name, sources=[])
        self.path = path

class RustBuildExt(build_ext):
    def build_extension(self, ext):
        if isinstance(ext, RustExtension):
            # Build the Rust library
            subprocess.check_call([
                "cargo", "build", "--release", "--manifest-path", ext.path
            ])
            
            # Copy the built library to the extension directory
            target_dir = os.path.dirname(self.get_ext_fullpath(ext.name))
            os.makedirs(target_dir, exist_ok=True)
            
            # Determine the library name based on platform
            if sys.platform.startswith("win"):
                lib_name = "codex_core.dll"
            elif sys.platform.startswith("darwin"):
                lib_name = "libcodex_core.dylib"
            else:
                lib_name = "libcodex_core.so"
            
            # Copy from target/release to the extension directory
            source = os.path.join(ext.path, "target", "release", lib_name)
            target = os.path.join(target_dir, f"{ext.name}.{lib_name.split('.')[-1]}")
            
            if os.path.exists(source):
                import shutil
                shutil.copy2(source, target)
                print(f"✅ Built and copied: {target}")
            else:
                raise FileNotFoundError(f"Rust library not found at {source}")
        else:
            super().build_extension(ext)

def main():
    # Read version from Cargo.toml
    cargo_toml = Path("Cargo.toml")
    version = "0.1.0"  # Default version
    
    if cargo_toml.exists():
        with open(cargo_toml, "r") as f:
            for line in f:
                if line.strip().startswith("version ="):
                    version = line.split("=")[1].strip().strip('"')
                    break
    
    setup(
        name="codex-core",
        version=version,
        description="Protected core module for ML pipeline with encrypted extraction rules",
        author="CodeX AI",
        author_email="support@codex.ai",
        url="https://github.com/stevensoma21/structured-pdf-parser",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: Other/Proprietary License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
        ],
        python_requires=">=3.8",
        ext_modules=[
            RustExtension("codex_core", ".")
        ],
        cmdclass={
            "build_ext": RustBuildExt,
        },
        packages=[],
        install_requires=[
            "cryptography>=3.4.0",
            "pycryptodome>=3.15.0",
        ],
        extras_require={
            "dev": [
                "pytest>=6.0",
                "black>=21.0",
                "mypy>=0.900",
            ],
        },
        include_package_data=True,
        package_data={
            "": ["assets/*"],
        },
        zip_safe=False,
    )

if __name__ == "__main__":
    main()
