@echo off

echo ========================================
echo  OpenEngine - Windows Setup
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11 from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python 3.10+ recommended
    echo Your version may work but is not tested
    echo.
)

echo Installing dependencies...
echo.

echo [1/4] Installing core packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install core packages
    pause
    exit /b 1
)

echo.
echo [2/4] Installing PyAudio (Windows-specific)...

pip install pipwin >nul 2>&1
if not errorlevel 1 (
    pipwin install pyaudio
    if not errorlevel 1 (
        echo [OK] PyAudio installed via pipwin
        goto :pyaudio_done
    )
)

pip install pyaudio
if errorlevel 1 (
    echo [WARNING] PyAudio installation failed
    echo.
    echo You may need to install it manually:
    echo 1. Install pipwin: pip install pipwin
    echo 2. Install PyAudio: pipwin install pyaudio
    echo.
    echo Or download pre-built wheel from:
    echo https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    echo.
) else (
    echo [OK] PyAudio installed
)

:pyaudio_done

echo.
echo [3/4] Installing vision packages...
cd vision
pip install -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Vision packages installation had issues
    echo Vision assistant may not work properly
)
cd ..

echo.
echo [4/4] Downloading YOLO models...
cd vision
python download_yolo.py
if errorlevel 1 (
    echo [WARNING] YOLO model download failed
    echo Vision features will not work without models
)
cd ..

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Test voice assistant: python voice_assistant.py
echo   2. Test vision assistant: python vision\vision_assistant.py
echo.
echo If you encounter issues, check windows\WINDOWS_INSTALL.md
echo.
pause
