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
- `app.py`: Minimal Windows desktop GUI wrapper (Tkinter)
- `build_exe.bat`: PyInstaller build helper for Windows `.exe`
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

## URL Input Support (Minimal Downloader)

`scripts/run_pipeline.py` supports two input modes:

- `--input <local-audio-file>`: Use an existing local file
- `--url <remote-source>`: Download first, then transcribe

### Supported `--url` types

- RSS 2.0 feed URL (uses latest episode with `<enclosure>`)
- Atom feed URL (uses latest entry with `rel="enclosure"`)
- Direct audio URL (e.g. `.mp3`, `.m4a`, `.wav`, `.aac`, `.ogg`)
- Direct audio response URL without file extension (detected by `Content-Type: audio/*`)

### `--url` behavior

- Downloads audio into `downloads/` under the current working directory
- Uses the latest file in `downloads/` as pipeline input after download succeeds
- Then writes transcript to `transcripts/`
- Then writes summary/highlights if requested

### Current limitations (important)

- Does **not** parse normal podcast episode webpages (HTML article pages)
- Does **not** support authenticated/private feeds
- Assumes "latest episode" means the first valid item returned by the feed
- Minimal feed parsing only (common RSS/Atom podcast patterns)

### Recommendation

- If you only have a webpage URL, first find the feed URL or direct audio URL
- If multiple episodes are needed, use your watcher (`main.py`) or call the downloader repeatedly

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

### Download + transcribe from direct audio URL

```powershell
python scripts/run_pipeline.py --url "https://cdn.example.com/episode.mp3" --model tiny --summarize
```

## Files To Read On Demand

- Whisper runtime/debugging issues: `references/whisper-troubleshooting.md`
- DeepSeek summary request/response shape: `references/deepseek-api.md`
- Output conventions: `references/output-format.md`
