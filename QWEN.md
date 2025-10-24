# CodeEnigma - Python Code Obfuscation Tool

## Project Overview

CodeEnigma is a lightweight, open-source tool for Python code obfuscation that helps protect your logic from reverse engineering and unauthorized access. It provides a secure way to distribute Python applications by encrypting the source code using AES-256 encryption and compiling the runtime into a Python extension module using Cython.

### Key Features
- Strong encryption using AES-256
- Simple API for obfuscating any Python module
- Secure and dynamic key generation
- Command-line interface for easy integration
- Expiration date support for obfuscated code
- Lightweight and dependency-minimal

### Architecture
The tool follows a modular architecture with several key components:
- **CLI Interface**: Built with Typer for user interaction
- **Orchestrator**: Coordinates the entire obfuscation process
- **Obfuscation Strategies**: Handles the actual encryption (currently AES-GCM)
- **Runtime Builder**: Creates the Cython-based runtime using AES-256 encryption
- **Extensions**: Add additional functionality like expiration dates
- **Bundler**: Package the obfuscated code as wheels (Poetry-based)

### Obfuscation Process
1. User provides a path to a Python module to obfuscate
2. CodeEnigma reads the module's source code
3. An AES-256 key is generated using a secure random number generator and set in `private.py`
4. Obfuscation runs file by file with these steps:
   - Compile using `compile(code, str(file_path), "exec")`
   - Compress the bytecode using `zlib.compress(compiled_code)`
   - Encode the compressed bytecode using `base64.b64encode(compressed_code)`
   - Encrypt the encoded bytecode using `AESGCM(SECRET_KEY).encrypt(NONCE, obfuscated, associated_data=None)`
5. CodeEnigma creates a new module with the obfuscated code
6. A `codeenigma_runtime.pyx` file is created with the deobfuscation logic
7. The runtime is compiled to a Python extension module using Cython
8. The final product is packaged as wheel files for distribution

## Building and Running

### Prerequisites
- Python >= 3.8, < 3.14
- Poetry (for development and building)
- System dependencies for Cython compilation

### Installation
```bash
# Using Poetry
poetry add codeenigma

# Using pip
pip install codeenigma
```

### Command Line Usage
```bash
# Basic obfuscation
codeenigma obfuscate /path/to/your/module

# With expiration date
codeenigma obfuscate /path/to/your/module -e "2025-12-31 23:59:59+0530"

# With custom output directory
codeenigma obfuscate /path/to/your/module -o custom_output

# Check version
codeenigma version
```

### Development Setup
```bash
# Clone the repository
git clone https://github.com/KrishnanSG/codeenigma.git
cd codeenigma

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run the CLI locally
poetry run codeenigma obfuscate /path/to/your/module
```

## Development Conventions

### Code Style
- Follows Google-style docstring conventions
- Uses Ruff for linting with specific configuration in `pyproject.toml`
- Line length follows black's default (though not enforced by Ruff in this project)
- Import organization using isort

### Architecture Patterns
- Strategy pattern for different obfuscation methods
- Builder pattern for runtime construction
- Template pattern for runtime code generation
- Extension system for adding new features

### Security Considerations
- AES-256 encryption for code protection
- Key obfuscation techniques using XOR operations and code generation
- Cython compilation to make reverse engineering harder
- Optional expiration date checks

### File Structure
```
codeenigma/
├── __init__.py          # Version management
├── cli.py              # Command-line interface
├── orchestrator.py     # Main workflow coordination
├── private.py          # Key generation and obfuscation
├── bundler/            # Wheel and extension building
├── extensions/         # Additional features (expiry, etc.)
├── runtime/            # Runtime compilation and building
├── strategies/         # Obfuscation algorithms
└── executor.py.template # Template for obfuscated files
```

## Testing
The project uses pytest for testing. Run tests with:
```bash
poetry run pytest
```

## Contributing
This is a free and open-source project. Contributions are welcome! If you have suggestions or find bugs, please open an issue on the GitHub repository.

# 偏好回答語系
請使用繁體中文