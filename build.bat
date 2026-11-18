@echo off
py -m pip install --upgrade pyinstaller winotify
set ICON=
if exist watcher.ico set ICON=--icon watcher.ico
py -m PyInstaller --onefile --clean --name watcher %ICON% --hidden-import winotify l4d2_watcher.py
echo.
echo Listo: dist\watcher.exe
pause
