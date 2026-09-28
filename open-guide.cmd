@echo off
rem Open the NHIMC Design Guide in the default browser. If it cannot be opened, copy it to Downloads.
set "GUIDE=%~dp0guide\nhimc-design-guide.html"
if not exist "%GUIDE%" (
  echo [ERROR] Design Guide not found: %GUIDE%
  exit /b 1
)
start "" "%GUIDE%"
if errorlevel 1 (
  copy /y "%GUIDE%" "%USERPROFILE%\Downloads\nhimc-design-guide.html" >nul
  echo [WARN] Could not open a browser. Saved a copy to %USERPROFILE%\Downloads\nhimc-design-guide.html
  exit /b 1
)
echo [OK] Design Guide opened.
