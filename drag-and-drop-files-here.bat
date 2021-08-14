@echo off
setlocal EnableDelayedExpansion
for %%f in (%*) do (
    set isValidFile=0
    if %%~xf==.json set isValidFile=1
    if %%~xf==.sm set isValidFile=1
    if !isValidFile!==1 python fnf-to-sm.py %%f
    if !isValidFile!==0 echo "%%~nxf" is not a valid file. File type must be JSON or SM.
    echo.
)
echo File conversion finished.
pause