import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe a podcast audio file with local Whisper.")
    parser.add_argument("--input", required=True, help="Path to audio file")
    parser.add_argument("--model", default="base", help="Whisper model (tiny/base/small/...)")
    parser.add_argument("--language", default="en", help="Source language")
    parser.add_argument("--output-dir", default="transcripts", help="Directory for transcript output")
    parser.add_argument("--format", default="txt", choices=["txt", "srt", "vtt", "tsv", "json", "all"])
    args = parser.parse_args()

    audio_path = Path(args.input)
    if not audio_path.exists():
        print(f"[error] input file not found: {audio_path}")
        return 1

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    # Avoid Windows console encoding crashes when Whisper prints help/errors.
    env.setdefault("PYTHONIOENCODING", "utf-8")

    cmd = [
        sys.executable,
        "-m",
        "whisper",
        str(audio_path),
        "--model",
        args.model,
        "--language",
        args.language,
        "--task",
        "transcribe",
        "--output_format",
        args.format,
        "--output_dir",
        str(out_dir),
        "--fp16",
        "False",
    ]
    print("[run]", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as exc:
        print(f"[error] whisper failed with code {exc.returncode}")
        return exc.returncode or 1

    txt_path = out_dir / f"{audio_path.stem}.txt"
    if txt_path.exists():
        print(f"[ok] transcript: {txt_path}")
    else:
        print(f"[ok] finished. Output written under: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

