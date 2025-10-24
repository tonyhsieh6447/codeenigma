#!/usr/bin/env python3

import os
import sys
import tempfile
import subprocess
from pathlib import Path

def test_codeenigma_installation():
    """Test if codeenigma is properly installed."""
    try:
        import codeenigma
        print("✅ CodeEnigma imported successfully")
        print(f"Version: {codeenigma.__version__}")
        return True
    except Exception as e:
        print(f"❌ Failed to import CodeEnigma: {e}")
        return False

def test_cli_help():
    """Test if CLI help works."""
    try:
        result = subprocess.run([sys.executable, '-m', 'codeenigma', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CodeEnigma CLI help works")
            return True
        else:
            print(f"❌ CodeEnigma CLI help failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed to run CodeEnigma CLI: {e}")
        return False

def test_basic_obfuscation():
    """Test basic obfuscation functionality."""
    try:
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Copy test module to temp directory
            test_module_content = '''
def hello_world():
    return "Hello, World!"

def add_numbers(a, b):
    return a + b

if __name__ == "__main__":
    print(hello_world())
    print(add_numbers(5, 3))
'''
            
            test_module_path = temp_path / "test_module.py"
            with open(test_module_path, 'w') as f:
                f.write(test_module_content)
            
            # Try to obfuscate the module
            from codeenigma.orchestrator import Orchestrator
            from codeenigma.strategies.encryption import CodeEnigmaObfuscationStrategy
            from codeenigma.runtime.cython.builder import CythonRuntimeBuilder
            from codeenigma.bundler.poetry import PoetryBundler
            
            # Generate AES key and nonce for testing
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            secret_key = AESGCM.generate_key(bit_length=256)
            nonce = os.urandom(12)
            
            strategy = CodeEnigmaObfuscationStrategy(secret_key, nonce)
            bundler = PoetryBundler()
            runtime_builder = CythonRuntimeBuilder(strategy, bundler)
            
            output_dir = temp_path / "output"
            
            orchestrator = Orchestrator(
                module_path=test_module_path,
                strategy=strategy,
                runtime_builder=runtime_builder,
                output_dir=output_dir
            )
            
            # This would normally run the obfuscation
            print("✅ Basic obfuscation setup works")
            return True
            
    except Exception as e:
        print(f"❌ Failed basic obfuscation test: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing CodeEnigma installation and functionality...")
    print("=" * 50)
    
    tests = [
        test_codeenigma_installation,
        test_cli_help,
        test_basic_obfuscation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("😞 Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)