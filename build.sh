#!/bin/bash
set -e

echo "Building obfuscated distribution..."

# Install PyArmor if needed
python3 -m pip install pyarmor

# Run obfuscation
python3 pyarmor_config.py

echo ""
echo "Build completed successfully!"
echo "Obfuscated code is ready in 'dist' directory"
echo ""
echo "Next steps:"
echo "1. Build Docker image: docker build -f Dockerfile.obfuscated -t your-app ."
echo "2. Test locally: docker run -p 8000:8000 your-app"
echo "3. Push to ECR using your CI/CD pipeline"