#!/usr/bin/env python3
"""
Fix spaCy installation issues with numpy compatibility.
This script resolves common spaCy installation problems.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {command.split()[0]}")
        return False


def check_current_installation():
    """Check current spaCy and numpy installation."""
    print("🔍 Checking current installation...")
    
    try:
        import numpy
        print(f"✅ NumPy version: {numpy.__version__}")
    except ImportError:
        print("❌ NumPy not installed")
        return False
    
    try:
        import spacy
        print(f"✅ spaCy version: {spacy.__version__}")
        return True
    except ImportError as e:
        print(f"❌ spaCy import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ spaCy installation issue: {e}")
        return False


def fix_numpy_compatibility():
    """Fix numpy compatibility issues."""
    print("🔧 Fixing numpy compatibility...")
    
    # Uninstall current numpy and spaCy
    commands = [
        ("poetry run pip uninstall -y numpy", "Uninstalling current numpy"),
        ("poetry run pip uninstall -y spacy", "Uninstalling current spaCy"),
        ("poetry run pip cache purge", "Clearing pip cache"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"⚠️  {description} failed, continuing...")
    
    # Install compatible versions
    install_commands = [
        ("poetry run pip install numpy>=1.24.0,<2.0.0", "Installing compatible numpy"),
        ("poetry run pip install spacy", "Installing spaCy"),
    ]
    
    for command, description in install_commands:
        if not run_command(command, description):
            return False
    
    return True


def test_spacy_import():
    """Test if spaCy can be imported successfully."""
    print("🧪 Testing spaCy import...")
    
    try:
        import spacy
        print(f"✅ spaCy {spacy.__version__} imported successfully")
        
        # Test basic functionality
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("This is a test sentence.")
        print(f"✅ spaCy basic functionality working (found {len(doc.ents)} entities)")
        
        return True
    except Exception as e:
        print(f"❌ spaCy import test failed: {e}")
        return False


def download_basic_models():
    """Download basic spaCy models for testing."""
    print("📦 Downloading basic spaCy models...")
    
    models = [
        ("en_core_web_sm", "English (small)"),
    ]
    
    for model, description in models:
        print(f"📦 Downloading {description} model: {model}")
        
        # Try spacy download
        command = f"poetry run python -m spacy download {model}"
        if not run_command(command, f"Downloading {model}"):
            print(f"⚠️  Failed to download {model} using spacy download")
            
            # Try pip install
            pip_command = f"poetry run pip install {model}"
            if not run_command(pip_command, f"Installing {model} via pip"):
                print(f"❌ Failed to install {model}")
                return False
    
    return True


def create_simple_test():
    """Create a simple test to verify the installation."""
    test_code = '''
import spacy

try:
    # Load a basic model
    nlp = spacy.load("en_core_web_sm")
    
    # Test with sample text
    text = "John Doe lives in Jakarta, Indonesia."
    doc = nlp(text)
    
    print("✅ spaCy test successful!")
    print(f"Text: {text}")
    print(f"Entities found: {len(doc.ents)}")
    
    for ent in doc.ents:
        print(f"  - {ent.text} ({ent.label_})")
        
except Exception as e:
    print(f"❌ spaCy test failed: {e}")
    sys.exit(1)
'''
    
    test_file = Path("test_spacy_simple.py")
    with open(test_file, "w") as f:
        f.write(test_code)
    
    print(f"✅ Created simple test file: {test_file}")
    return test_file


def main():
    """Main function to fix spaCy installation."""
    print("🚀 spaCy Installation Fixer")
    print("=" * 40)
    
    # Check current installation
    if check_current_installation():
        print("✅ spaCy is already working correctly!")
        return True
    
    # Fix numpy compatibility
    if not fix_numpy_compatibility():
        print("❌ Failed to fix numpy compatibility")
        return False
    
    # Test spaCy import
    if not test_spacy_import():
        print("❌ spaCy import test failed after fix")
        return False
    
    # Download basic models
    if not download_basic_models():
        print("❌ Failed to download basic models")
        return False
    
    # Create and run simple test
    test_file = create_simple_test()
    print(f"🧪 Running simple test...")
    
    if run_command(f"poetry run python {test_file}", "Running spaCy test"):
        print("🎉 spaCy installation fixed successfully!")
        
        # Clean up test file
        test_file.unlink()
        
        print("\n📋 Next steps:")
        print("1. Run: poetry run python scripts/download_spacy_models.py")
        print("2. Test extraction: poetry run python test_spacy_extraction.py")
        
        return True
    else:
        print("❌ spaCy test failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 