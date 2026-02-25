import argparse
import json
import os
import urllib.request
from pathlib import Path


def deepseek_chat(api_key: str, api_base: str, model: str, messages: list[dict]) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        api_base.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode("utf-8", errors="ignore"))
    return body["choices"][0]["message"]["content"].strip()


def chunk_text(text: str, max_chars: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end])
        start = end
    return chunks


def summarize_transcript(
    *,
    api_key: str,
    api_base: str,
    model: str,
    transcript_text: str,
    max_chars: int,
    mode: str,
) -> str:
    if mode == "highlights":
        part_system = "You are a Chinese podcast editor. Extract high-value Chinese highlights from transcript chunks."
        part_user_tpl = (
            "Read transcript chunk {idx}. Output Chinese notes focused on high-signal content only:\n"
            "1) 核心观点\n2) 关键案例/证据\n3) 值得引用的表达（意译）\n4) 风险/争议点\n\n{chunk}"
        )
        merge_system = "You are a senior Chinese editor. Produce a polished Chinese 'essence summary'."
        merge_user_tpl = (
            "Merge the chunk notes into one Chinese essence summary for a podcast.\n"
            "Use this structure exactly:\n"
            "## 一句话结论\n"
            "## 核心观点（6-12条）\n"
            "## 关键细节与案例\n"
            "## 风险与争议\n"
            "## 可行动启发（面向产品/工程/创业）\n"
            "## 适合二次创作的选题角度（5条）\n\n"
            "Chunk notes:\n\n{combined}"
        )
    else:
        part_system = "You are a Chinese podcast editor. Return concise but informative Chinese chunk summaries."
        part_user_tpl = (
            "Summarize transcript chunk {idx} in Chinese. Include:\n"
            "1) 主题\n2) 主要观点\n3) 关键事实/案例\n4) 可执行建议（如果有）\n\n{chunk}"
        )
        merge_system = "You are a Chinese podcast editor. Produce a structured final Chinese summary."
        merge_user_tpl = (
            "Merge the chunk summaries into one final Chinese summary.\n"
            "Use sections: Key Points, Conclusions, Actionable Ideas.\n\n{combined}"
        )

    chunks = chunk_text(transcript_text, max_chars=max_chars)
    partials: list[str] = []
    for idx, chunk in enumerate(chunks, 1):
        partials.append(
            deepseek_chat(
                api_key,
                api_base,
                model,
                [
                    {"role": "system", "content": part_system},
                    {"role": "user", "content": part_user_tpl.format(idx=idx, chunk=chunk)},
                ],
            )
        )

    combined = "\n\n".join(f"[Part {i}]\n{p}" for i, p in enumerate(partials, 1))
    return deepseek_chat(
        api_key,
        api_base,
        model,
        [
            {"role": "system", "content": merge_system},
            {"role": "user", "content": merge_user_tpl.format(combined=combined)},
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a transcript in Chinese using DeepSeek.")
    parser.add_argument("--input", required=True, help="Transcript txt path")
    parser.add_argument("--output", default="", help="Output markdown path")
    parser.add_argument(
        "--mode",
        default="summary",
        choices=["summary", "highlights"],
        help="summary=structured summary, highlights=Chinese essence summary",
    )
    parser.add_argument("--api-base", default=os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"))
    parser.add_argument("--model", default=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"))
    parser.add_argument("--max-chars", type=int, default=8000, help="Chunk size for transcript processing")
    args = parser.parse_args()

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("[error] DEEPSEEK_API_KEY is not set")
        return 1

    transcript_path = Path(args.input)
    if not transcript_path.exists():
        print(f"[error] transcript not found: {transcript_path}")
        return 1

    text = transcript_path.read_text(encoding="utf-8", errors="ignore")
    if not text.strip():
        print("[error] transcript is empty")
        return 1

    summary = summarize_transcript(
        api_key=api_key,
        api_base=args.api_base,
        model=args.model,
        transcript_text=text,
        max_chars=args.max_chars,
        mode=args.mode,
    )

    if args.output:
        out_path = Path(args.output)
    else:
        out_dir = Path("summaries" if args.mode == "summary" else "highlights")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (transcript_path.stem + ".md")

    out_path.write_text(f"# {transcript_path.stem}\n\n{summary}\n", encoding="utf-8")
    print(f"[ok] {args.mode}: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
