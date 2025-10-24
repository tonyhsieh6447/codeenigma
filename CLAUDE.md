# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CodeEnigma is a lightweight, open-source Python code obfuscation tool that encrypts Python source code using AES-256 encryption. It compiles source to bytecode, compresses, encrypts, and packages the obfuscated code with a Cython-compiled runtime for distribution as wheel files.

**Purpose**: Protect Python code from reverse engineering while providing a transparent, open-source alternative to tools like PyArmor.

**Python Support**: 3.8 - 3.13

## Development Commands

### Setup
```bash
# Install dependencies
poetry install --all-extras

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
```

### Testing
```bash
# Run all tests
poetry run pytest tests

# Run tests with coverage
poetry run coverage run -m pytest tests
poetry run coverage report
poetry run coverage html

# Run tests in parallel (requires pytest-xdist)
poetry run pytest tests -n auto
```

### Linting
```bash
# Run linting checks with ruff
poetry run ruff check .

# Auto-fix linting issues
poetry run ruff check --fix .

# Format code
poetry run ruff format .
```

### Building
```bash
# Build package distribution
poetry build

# Install package locally for testing
poetry install
```

### Running CLI
```bash
# After poetry install, the CLI is available as:
codeenigma obfuscate /path/to/module

# With options:
codeenigma obfuscate /path/to/module -e "2025-12-31 23:59:59+0530" -o custom_output

# Check version
codeenigma version
```

## Architecture Overview

CodeEnigma follows a modular pipeline architecture with clear separation of concerns:

```
CLI → Orchestrator → [Strategy, RuntimeBuilder, Bundler, Extensions]
```

### Core Components

1. **Orchestrator** ([orchestrator.py](codeenigma/orchestrator.py))
   - Central workflow coordinator
   - Manages 3-phase process: obfuscation → runtime building → wheel packaging
   - Key methods: `run_obfuscation()`, `build_obfuscated_wheel()`, `run()`

2. **Strategy** ([strategies/encryption.py](codeenigma/strategies/encryption.py))
   - Implements obfuscation logic: compile → marshal → compress → encode → encrypt
   - Uses AES-256-GCM encryption with secure key generation
   - Base class: `BaseObfuscationStrategy` (abstract)

3. **Runtime Builder** ([runtime/cython/builder.py](codeenigma/runtime/cython/builder.py))
   - Generates Cython-compiled deobfuscation runtime
   - Creates `codeenigma_runtime.pyx` and compiles to `.so` shared object
   - Packages runtime as distributable wheel
   - Base class: `IRuntimeBuilder` (abstract)

4. **Bundler** ([bundler/poetry.py](codeenigma/bundler/poetry.py))
   - Handles wheel building using Poetry
   - Compiles Cython extensions
   - Base class: `IBundler` (interface)

5. **Extensions** ([extensions/expiry.py](codeenigma/extensions/expiry.py))
   - Plugin system for additional features
   - `ExpiryExtension`: Injects time-based expiration checks
   - Base class: `IExtension` (abstract)

6. **Private Key Management** ([private.py](codeenigma/private.py))
   - Generates AES-256 keys using `AESGCM.generate_key()`
   - Obfuscates keys by splitting into parts and applying XOR operations
   - Generates runtime key reconstruction code

### Obfuscation Pipeline

```
Python Source (.py)
  ↓ compile()
Code Object
  ↓ marshal.dumps()
Bytecode
  ↓ zlib.compress()
Compressed Bytecode
  ↓ base64.b64encode()
Encoded Bytecode
  ↓ AESGCM.encrypt(SECRET_KEY, NONCE, data)
Encrypted Bytecode (stored in obfuscated .py)
```

### Runtime Execution Flow

```
Obfuscated Module Import
  ↓
executor.py.template wraps call
  ↓
from codeenigma_runtime import execute_secure_code
  ↓
Reconstruct SECRET_KEY from obfuscated parts
  ↓
Decrypt → Base64 decode → Decompress → Unmarshal
  ↓
Execute original code object
  ↓
Optional: Check expiry date
```

### Template System

CodeEnigma uses Python string templates for code generation:

- **[executor.py.template](codeenigma/executor.py.template)**: Wrapper for each obfuscated module file
- **[encryption_runtime.py.template](codeenigma/strategies/encryption_runtime.py.template)**: Deobfuscation logic in Cython
- **[expiry_code.py.template](codeenigma/extensions/expiry_code.py.template)**: Time-based expiry checking
- **Cython templates** in [runtime/cython/](codeenigma/runtime/cython/): `setup.py.template`, `pyproject.toml.template`, `init.py.template`

## Key Design Patterns

- **Strategy Pattern**: Obfuscation strategies, bundlers, runtime builders are swappable implementations
- **Template Pattern**: Template-based code generation for flexibility
- **Composition**: Orchestrator composes strategy, bundler, extensions, runtime
- **Plugin Architecture**: Extensions inject additional functionality into runtime

## Output Structure

Running `codeenigma obfuscate /path/to/module` produces:

```
cedist/  (or custom output directory)
├── obfuscated_module/
│   ├── __init__.py  (obfuscated)
│   ├── main.py      (obfuscated)
│   └── ...          (all .py files obfuscated)
├── codeenigma_runtime-*.whl  (deobfuscation runtime)
└── module_name-*.whl         (obfuscated module package)
```

## Testing Strategy

- Framework: pytest with unittest.TestCase
- Tests located in [tests/](tests/)
- [test_e2e.py](tests/test_e2e.py): End-to-end integration tests using example module
- [test_version.py](tests/test_version.py): Version metadata verification
- Coverage configured to omit `tests/*`, `setup.py`, `*/__init__.py`

### Running Specific Tests

```bash
# Run single test file
poetry run pytest tests/test_e2e.py

# Run single test function
poetry run pytest tests/test_e2e.py::TestObfuscation::test_obfuscate

# Run with verbose output
poetry run pytest tests -v
```

## Code Style

- Linter: Ruff with strict rules (E, W, F, I, B, C4, UP)
- Docstring convention: Google style
- Line length: Flexible (E501 ignored)
- Import style: Combined as imports, not forced single-line

## Important Implementation Notes

### Security
- AES-256-GCM encryption with 96-bit NONCE
- Keys are obfuscated by splitting into 4 parts, XORing parts 0 and 3, reversing part 1
- Key reconstruction code is embedded in compiled Cython runtime

### Workflow Phases
The orchestrator runs 3 distinct phases:
1. **Obfuscation Phase**: Iterates through all `.py` files in module, encrypts each
2. **Runtime Building Phase**: Compiles `codeenigma_runtime.pyx` to `.so`, packages as wheel
3. **Wheel Building Phase**: Packages obfuscated module as distributable wheel

### Template Substitution
Templates use `$variable` syntax for substitution. Key variables:
- `$secure_code`: Encrypted bytecode in executor template
- `$SECRET_KEY_PART_*`: Obfuscated key parts in runtime template
- `$EXPIRY_DATE`: Expiration timestamp in expiry extension

### Cython Compilation
Runtime is compiled to platform-specific `.so` (Linux/macOS) or `.pyd` (Windows) extension module. This makes reverse engineering the decryption logic significantly harder.

**IMPORTANT**: The compiled `.so` file MUST export `PyInit_codeenigma_runtime` symbol for Python to load it. The following compiler/linker flags have been carefully configured:
- **Removed** `-fvisibility=hidden`: Would hide all symbols including PyInit
- **Removed** `-flto`: Link-time optimization can cause symbol issues
- **Removed** `--strip-all`: Would remove all symbols including PyInit
- **Disabled** `strip` command: Preserves all necessary symbols

The build process now includes symbol verification to ensure `PyInit_codeenigma_runtime` is present.

## Dependencies

**Core**:
- `cryptography`: AES-GCM encryption
- `typer[all]`: CLI framework with rich output
- `Cython`: Runtime compilation
- `setuptools`: Extension building

**Dev**:
- `pytest`, `pytest-cov`, `pytest-xdist`: Testing
- `ruff`: Linting and formatting
- `coverage`: Coverage reporting

## CI/CD

GitHub Actions workflow ([.github/workflows/main.yml](.github/workflows/main.yml)):
- Tests on Python 3.8-3.13 (3.13 is experimental)
- Coverage reporting for Python 3.12
- Uses Poetry for dependency management
- Runs: `poetry run coverage run -m pytest tests`
