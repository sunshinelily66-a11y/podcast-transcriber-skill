import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], env: dict | None = None) -> int:
    print("[run]", " ".join(cmd))
    return subprocess.run(cmd, env=env).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe a podcast and optionally summarize it.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="Local audio path")
    group.add_argument("--url", help="RSS feed URL or direct audio URL")
    parser.add_argument("--model", default="base", help="Whisper model")
    parser.add_argument("--language", default="en", help="Whisper language")
    parser.add_argument("--summarize", action="store_true", help="Generate DeepSeek Chinese summary")
    parser.add_argument(
        "--highlights",
        action="store_true",
        help="Generate Chinese essence summary (highlights). Implied when --summarize is set.",
    )
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    scripts_dir = skill_dir / "scripts"
    transcript_dir = Path.cwd() / "transcripts"
    transcript_dir.mkdir(exist_ok=True)
    download_dir = Path.cwd() / "downloads"
    download_dir.mkdir(exist_ok=True)

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")

    audio_input = args.input
    if args.url:
        code = run(
            [
                sys.executable,
                str(scripts_dir / "download_podcast.py"),
                "--url",
                args.url,
                "--output-dir",
                str(download_dir),
            ],
            env=env,
        )
        if code != 0:
            return code
        # Pick the latest file in downloads as the just-downloaded file.
        candidates = sorted(download_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            print("[error] download step reported success but no file found")
            return 1
        audio_input = str(candidates[0])

    code = run(
        [
            sys.executable,
            str(scripts_dir / "transcribe_podcast.py"),
            "--input",
            audio_input,
            "--model",
            args.model,
            "--language",
            args.language,
            "--output-dir",
            str(transcript_dir),
        ],
        env=env,
    )
    if code != 0:
        return code

    transcript_path = transcript_dir / (Path(audio_input).stem + ".txt")
    if not args.summarize and not args.highlights:
        print(f"[ok] transcript ready: {transcript_path}")
        return 0

    if not transcript_path.exists():
        print(f"[error] transcript not found for summary: {transcript_path}")
        return 1

    final_code = 0
    if args.summarize:
        final_code = run(
            [
                sys.executable,
                str(scripts_dir / "summarize_deepseek.py"),
                "--input",
                str(transcript_path),
                "--mode",
                "summary",
            ],
            env=env,
        )
        if final_code != 0:
            return final_code

    if args.highlights or args.summarize:
        final_code = run(
            [
                sys.executable,
                str(scripts_dir / "summarize_deepseek.py"),
                "--input",
                str(transcript_path),
                "--mode",
                "highlights",
            ],
            env=env,
        )

    return final_code


if __name__ == "__main__":
    raise SystemExit(main())
