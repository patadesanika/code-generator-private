@echo off
echo Building obfuscated distribution...

REM Install PyArmor if needed
python -m pip install pyarmor

REM Run obfuscation
python pyarmor_config.py

if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    exit /b 1
)

echo.
echo Build completed successfully!
echo Obfuscated code is ready in 'dist' directory
echo.
echo Next steps:
echo 1. Build Docker image: docker build -f Dockerfile.obfuscated -t your-app .
echo 2. Test locally: docker run -p 8000:8000 your-app
echo 3. Push to ECR using your CI/CD pipeline