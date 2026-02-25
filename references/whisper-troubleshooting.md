# Whisper Troubleshooting (Windows)

## Common failure modes

### 1) `import torch` fails with `c10.dll` / `WinError 1114`

Cause:
- PyTorch DLL dependency failed to initialize (often VC++ runtime, broken install, or incompatible wheel).

Fix:
1. Install/repair VC++ 2015-2022 x64 redistributable.
2. Reinstall CPU wheels from official index:
   - `python3 -m pip install --upgrade --force-reinstall torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`
3. Verify:
   - `python3 -c "import torch; print(torch.__version__)"`

### 2) `python3 -m whisper --help` throws `UnicodeEncodeError` on GBK console

Cause:
- Whisper help text contains characters Windows GBK console cannot print.

Fix:
- Set `PYTHONIOENCODING=utf-8` for the command.
- Redirect output to file if needed.

Example:
- `$env:PYTHONIOENCODING='utf-8'; python3 -m whisper --help > whisper_help.txt`

### 3) Transcription appears "stuck" or times out

Cause:
- CPU transcription of long episodes with `small` model is slow.

Fix:
- Test with `tiny` or `base` first.
- Increase timeout or run without timeout.
- Use `--download-only` in the watcher when transcription is unstable.

## Alternatives when local Whisper is too slow or unstable

### Option A: Faster local path
- Use `tiny` or `base`.
- Split long audio into chunks with ffmpeg and transcribe chunks.

### Option B: Local GUI tools (less coding)
- Subtitle Edit (Whisper backend support)
- whisper.cpp binaries (CPU-friendly)
- Faster-Whisper (CTranslate2, often faster than original Whisper on CPU)

### Option C: Cloud transcription API (paid)
- Deepgram
- AssemblyAI
- OpenAI audio transcription

Tradeoff:
- Cloud APIs are faster and simpler to run, but cost money and require uploading audio.

