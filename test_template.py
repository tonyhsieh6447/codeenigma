#!/usr/bin/env python3

import tempfile
import os
from pathlib import Path
from string import Template

def test_template():
    """Test if the template is correctly updated"""
    template_path = Path("/Users/tonyhsieh/Documents/code/thsieh/codeenigma/codeenigma/runtime/cython/init.py.template")
    
    with open(template_path, 'r') as f:
        content = f.read()
        
    print("Current template content:")
    print(content)
    
    # Check if the new import statement is present
    if "from . import execute_secure_code" in content:
        print("\n✅ Template has been correctly updated")
        return True
    else:
        print("\n❌ Template has NOT been updated")
        return False

if __name__ == "__main__":
    test_template()