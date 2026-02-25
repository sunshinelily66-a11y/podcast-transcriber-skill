---
name: podcast-transcriber
description: Transcribe podcast audio files with local Whisper and optionally create Chinese summaries with DeepSeek API. Use when Codex needs to convert podcast audio (.mp3/.m4a/.wav) to text, debug Whisper environment issues on Windows, or produce a transcript-plus-summary pipeline for downloaded podcast episodes.
---

# Podcast Transcriber

Use this skill to run a local-first podcast transcription workflow.

## Bundled Resources

- `scripts/check_env.ps1`: Validate local environment (`python3`, `torch`, `ffmpeg`, `whisper`)
- `scripts/transcribe_podcast.py`: Local Whisper transcription entrypoint
- `scripts/download_podcast.py`: Download latest episode from RSS or download direct audio URL
- `scripts/summarize_deepseek.py`: DeepSeek Chinese summary/highlights generator
- `scripts/run_pipeline.py`: End-to-end pipeline (transcript + summary + highlights)
- `references/whisper-troubleshooting.md`: Windows/Whisper runtime troubleshooting and fallback paths
- `references/deepseek-api.md`: DeepSeek request/response notes
- `references/output-format.md`: Output file locations and conventions

## Quick Start

Run commands from the skill directory (`podcast-transcriber/`) unless noted otherwise.

1. Run environment checks first:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check_env.ps1
```

2. Transcribe locally with Whisper:

```powershell
python scripts/transcribe_podcast.py --input "downloads\episode.mp3" --model base
```

3. Optional Chinese summary with DeepSeek:

```powershell
python scripts/summarize_deepseek.py --input "..\transcripts\episode.txt" --mode summary
```

4. Chinese essence highlights (higher signal, better for notes/content reuse):

```powershell
python scripts/summarize_deepseek.py --input "..\transcripts\episode.txt" --mode highlights
```

5. Or run the pipeline:

```powershell
python scripts/run_pipeline.py --input "..\downloads\episode.mp3" --model base --summarize
```

6. Run pipeline directly from RSS or audio URL (minimal download support):

```powershell
python scripts/run_pipeline.py --url "https://example.com/podcast/feed.xml" --model tiny --summarize
python scripts/run_pipeline.py --url "https://cdn.example.com/episode.mp3" --model tiny
```

`--summarize` now produces both:
- `summaries/<stem>.md` (standard summary)
- `highlights/<stem>.md` (Chinese essence summary)

## Workflow Rules

- Start with `tiny` or `base` to validate the pipeline on long episodes before switching to `small`.
- Prefer `--download-only` in the main watcher if Whisper is failing; do not block downloading on transcription.
- On Windows console encoding issues, set `PYTHONIOENCODING=utf-8` for Whisper CLI commands.
- If local Whisper is too slow or unstable, read `references/whisper-troubleshooting.md` and switch to an alternative path.
- For very long episodes on CPU, validate quality/speed with a short clip first, then process the full file.

## Common Invocations

### Full episode, local transcription only

```powershell
python scripts/run_pipeline.py --input "..\downloads\episode.mp3" --model tiny
```

### Full episode, transcript + summary + highlights

```powershell
python scripts/run_pipeline.py --input "..\downloads\episode.mp3" --model tiny --summarize
```

### Generate highlights from an existing transcript (no retranscription)

```powershell
python scripts/summarize_deepseek.py --input "..\transcripts\episode.txt" --mode highlights
```

### Download + transcribe from RSS feed URL

```powershell
python scripts/run_pipeline.py --url "https://example.com/feed.xml" --model tiny --summarize
```

## Files To Read On Demand

- Whisper runtime/debugging issues: `references/whisper-troubleshooting.md`
- DeepSeek summary request/response shape: `references/deepseek-api.md`
- Output conventions: `references/output-format.md`
