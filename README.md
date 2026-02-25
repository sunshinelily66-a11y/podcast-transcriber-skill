# Podcast Transcriber Skill

Local-first podcast transcription skill for Codex:

- Transcribe podcast audio with local Whisper
- Generate Chinese summaries with DeepSeek API
- Generate Chinese "essence highlights" for fast review / secondary content creation

## What It Includes

- `SKILL.md`: Skill instructions and workflow
- `scripts/check_env.ps1`: Environment checks (`python3`, `torch`, `ffmpeg`, `whisper`)
- `scripts/transcribe_podcast.py`: Local Whisper transcription
- `scripts/summarize_deepseek.py`: DeepSeek summary / highlights generation
- `scripts/run_pipeline.py`: End-to-end pipeline
- `references/`: Troubleshooting and output docs

## Quick Start

Run from this repository root.

1. Check environment

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check_env.ps1
```

2. Transcribe only (fast validation with `tiny`)

```powershell
python3 scripts/run_pipeline.py --input "..\\downloads\\episode.mp3" --model tiny
```

3. Transcribe + summary + highlights

```powershell
python3 scripts/run_pipeline.py --input "..\\downloads\\episode.mp3" --model tiny --summarize
```

4. Generate highlights from an existing transcript

```powershell
python3 scripts/summarize_deepseek.py --input "..\\transcripts\\episode.txt" --mode highlights
```

## Outputs

- Transcript: `transcripts/<audio-stem>.txt`
- Summary: `summaries/<audio-stem>.md`
- Highlights: `highlights/<audio-stem>.md`

## Environment Requirements

- `python3`
- `ffmpeg`
- `openai-whisper` (local)
- `torch` (CPU version is fine)
- `DEEPSEEK_API_KEY` (for summary/highlights only)

## Notes

- On Windows, console encoding may break Whisper help output. Use:

```powershell
$env:PYTHONIOENCODING="utf-8"
```

- Long episodes on CPU can take a long time. Start with `tiny` or `base`.

