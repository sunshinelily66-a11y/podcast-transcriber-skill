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
    parser.add_argument("--input", required=True, help="Audio path")
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

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")

    code = run(
        [
            sys.executable,
            str(scripts_dir / "transcribe_podcast.py"),
            "--input",
            args.input,
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

    transcript_path = transcript_dir / (Path(args.input).stem + ".txt")
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
