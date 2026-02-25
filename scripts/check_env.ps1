Write-Host "== Python =="
python3 --version

Write-Host "`n== Torch =="
python3 -c "import torch; print(torch.__version__); print('cuda:', torch.cuda.is_available())"

Write-Host "`n== FFmpeg =="
ffmpeg -version | Select-Object -First 1

Write-Host "`n== Whisper module =="
$env:PYTHONIOENCODING = "utf-8"
python3 -m whisper --help *> $null
if ($LASTEXITCODE -eq 0) {
  Write-Host "whisper: OK"
} else {
  Write-Host "whisper: FAILED (see references/whisper-troubleshooting.md)"
  exit 1
}

