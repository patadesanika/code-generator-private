# PyArmor Code Obfuscation Setup

This repository now includes PyArmor code obfuscation for production deployment.

## Quick Start

### 1. Build Obfuscated Code
```bash
# Windows
build.bat

# Ubuntu/Linux
chmod +x build.sh
./build.sh

# Or directly:
python3 pyarmor_config.py
```

### 2. Test Locally
```bash
# Build and test Docker image
python test_obfuscated.py

# Or manually:
docker build -f Dockerfile.obfuscated -t my-app .
docker run -p 8000:8000 my-app
```

### 3. Deploy to ECR
Your existing CI/CD pipeline will automatically:
- Obfuscate code using PyArmor
- Build Docker image with obfuscated code
- Push to ECR

## What Gets Obfuscated

- `main.py` - Main FastAPI application
- `lambda_function.py` - Lambda handler
- `utils/` - All utility modules
  - `event_messages.py`
  - `kafka.py`
  - `observed.py`

## Files Structure

```
├── pyarmor_config.py      # Obfuscation script
├── Dockerfile.obfuscated  # Production Dockerfile
├── build.bat             # Windows build script
├── build.sh              # Ubuntu/Linux build script
├── test_obfuscated.py    # Test script
└── dist/                 # Generated obfuscated code
    ├── main.py           # Obfuscated main app
    ├── utils/            # Obfuscated utilities
    └── requirements.txt  # Dependencies
```

## CI/CD Integration

The GitHub Actions workflow automatically:
1. Installs PyArmor
2. Runs obfuscation
3. Builds Docker image with obfuscated code
4. Pushes to ECR

## Security Benefits

- Source code is obfuscated and protected
- Runtime performance maintained
- Original functionality preserved
- Reverse engineering difficulty increased

## Troubleshooting

### Build Issues
```bash
# Ubuntu - Install PyArmor manually
python3 -m pip install pyarmor

# Clean build
rm -rf dist/
python3 pyarmor_config.py

# Make build script executable
chmod +x build.sh
```

### Docker Issues
```bash
# Check obfuscated files exist
ls dist/

# Test build step by step
docker build -f Dockerfile.obfuscated -t test-app .
docker run --rm test-app python -c "import main; print('OK')"
```