#!/usr/bin/env python3
"""
PyArmor configuration and build script for code obfuscation
"""
import os
import shutil
import subprocess
import sys

def setup_pyarmor():
    """Install PyArmor if not already installed"""
    try:
        import pyarmor
        print("PyArmor already installed")
    except ImportError:
        print("Installing PyArmor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyarmor"])

def obfuscate_code():
    """Obfuscate the Python code using PyArmor"""
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Create dist directory
    os.makedirs("dist", exist_ok=True)
    
    # Files to obfuscate
    source_files = [
        "main.py",
        "lambda_function.py",
        "utils/event_messages.py",
        "utils/kafka.py", 
        "utils/observed.py"
    ]
    
    # Copy non-Python files
    non_python_files = [
        "requirements.txt",
        ".env.example",
        "Dockerfile",
        "DockerfileLambda"
    ]
    
    print("Obfuscating Python files...")
    
    # Obfuscate main files
    cmd = [
        "pyarmor", "gen", 
        "--output", "dist",
        "--recursive"
    ] + source_files
    
    try:
        subprocess.check_call(cmd)
        print("✓ Code obfuscation completed")
    except subprocess.CalledProcessError as e:
        print(f"✗ Obfuscation failed: {e}")
        return False
    
    # Copy non-Python files to dist
    for file in non_python_files:
        if os.path.exists(file):
            shutil.copy2(file, "dist/")
    
    # Copy utils directory structure (if any non-Python files exist)
    if os.path.exists("utils"):
        os.makedirs("dist/utils", exist_ok=True)
    
    print("✓ Distribution created in 'dist' directory")
    return True

if __name__ == "__main__":
    setup_pyarmor()
    if obfuscate_code():
        print("\n🎉 Build completed successfully!")
        print("📁 Obfuscated code is in the 'dist' directory")
        print("🐳 Ready for Docker build")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)