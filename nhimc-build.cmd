@echo off
rem Drag a Content-only source.html onto this file to build a verified index.html next to it.
if "%~1"=="" (
  echo Usage: drag source.html onto nhimc-build.cmd
  pause
  exit /b 1
)
python "%~dp0scripts\build_verified_artifact.py" --input "%~1" --output "%~dp1index.html"
pause
