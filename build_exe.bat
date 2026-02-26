@echo off
setlocal

REM Build a Windows .exe for the Tkinter app (run from repository root)
python3 -m pip install pyinstaller
python3 -m PyInstaller --noconfirm --onefile --windowed --name PodcastTranscriber app.py

echo.
echo Build finished. Check dist\PodcastTranscriber.exe

