#!/usr/bin/env python3
"""
Test script to verify obfuscated code works correctly
"""
import os
import sys
import subprocess
import time
import requests

def test_obfuscated_build():
    """Test the obfuscated application"""
    
    print("🧪 Testing obfuscated build...")
    
    # Check if dist directory exists
    if not os.path.exists("dist"):
        print("❌ No dist directory found. Run 'python pyarmor_config.py' first")
        return False
    
    # Check if main files exist in dist
    required_files = ["main.py", "requirements.txt"]
    for file in required_files:
        if not os.path.exists(f"dist/{file}"):
            print(f"❌ Missing file in dist: {file}")
            return False
    
    print("✓ Obfuscated files found")
    
    # Test Docker build
    print("🐳 Testing Docker build...")
    try:
        subprocess.check_call([
            "docker", "build", 
            "-f", "Dockerfile.obfuscated", 
            "-t", "test-obfuscated-app", 
            "."
        ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print("✓ Docker build successful")
    except subprocess.CalledProcessError:
        print("❌ Docker build failed")
        return False
    
    # Test container run (optional - requires Docker)
    print("🚀 Testing container startup...")
    try:
        # Start container in background
        container = subprocess.Popen([
            "docker", "run", "--rm", "-p", "8001:8000", 
            "test-obfuscated-app"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for startup
        time.sleep(5)
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:8001/docs", timeout=5)
            if response.status_code == 200:
                print("✓ Container is running and responding")
                success = True
            else:
                print("❌ Container not responding correctly")
                success = False
        except requests.RequestException:
            print("❌ Cannot connect to container")
            success = False
        
        # Stop container
        container.terminate()
        container.wait()
        
        return success
        
    except Exception as e:
        print(f"❌ Container test failed: {e}")
        return False

if __name__ == "__main__":
    if test_obfuscated_build():
        print("\n🎉 All tests passed! Ready for ECR deployment")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)