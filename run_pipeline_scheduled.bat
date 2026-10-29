@echo off
setlocal EnableExtensions

REM Update this path if your project folder is elsewhere.
set "PROJECT_DIR=%USERPROFILE%\Documents\emerging-markets-intelligence"
set "LOG_DIR=%PROJECT_DIR%\logs"
set "PIPELINE_SCRIPT=%PROJECT_DIR%\run_pipeline.py"

if not exist "%PROJECT_DIR%" (
    echo ERROR: Project folder not found: "%PROJECT_DIR%"
    exit /b 2
)

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Timestamp suitable for filenames on Windows.
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set "STAMP=%%i"
set "LOG_FILE=%LOG_DIR%\pipeline_%STAMP%.log"

echo ============================================================
echo Emerging Markets Intelligence - Scheduled Pipeline
echo Started: %DATE% %TIME%
echo Project: %PROJECT_DIR%
echo Log: %LOG_FILE%
echo ============================================================

(
    echo Started: %DATE% %TIME%
    echo Project: %PROJECT_DIR%
    echo.

    if not exist "%PIPELINE_SCRIPT%" (
        echo ERROR: run_pipeline.py was not found at "%PIPELINE_SCRIPT%"
        exit /b 3
    )

    REM Prefer the project's virtual environment, if present.
    if exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (
        set "PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe"
    ) else if exist "%PROJECT_DIR%\venv\Scripts\python.exe" (
        set "PYTHON_EXE=%PROJECT_DIR%\venv\Scripts\python.exe"
    ) else (
        set "PYTHON_EXE=python"
    )

    echo Python executable: %PYTHON_EXE%
    echo Running pipeline...
    echo.

    "%PYTHON_EXE%" "%PIPELINE_SCRIPT%"
    set "PIPELINE_EXIT_CODE=%ERRORLEVEL%"

    echo.
    echo Finished: %DATE% %TIME%
    echo Exit code: %PIPELINE_EXIT_CODE%

    if not "%PIPELINE_EXIT_CODE%"=="0" (
        echo STATUS: FAILED
        exit /b %PIPELINE_EXIT_CODE%
    )

    echo STATUS: SUCCESS
) >> "%LOG_FILE%" 2>&1

set "FINAL_CODE=%ERRORLEVEL%"
echo Completed with exit code %FINAL_CODE%.
echo Review log: %LOG_FILE%
exit /b %FINAL_CODE%
