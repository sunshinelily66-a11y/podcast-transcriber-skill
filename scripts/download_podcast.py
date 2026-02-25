import argparse
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse


USER_AGENT = "podcast-transcriber-skill/1.0"


def fetch_bytes(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        content_type = resp.headers.get("Content-Type", "")
        data = resp.read()
    return data, content_type.lower()


def safe_filename(name: str) -> str:
    name = re.sub(r"\s+", " ", name).strip()
    name = re.sub(r"[^\w\s-]", "", name)
    name = name.replace(" ", "_")
    return (name[:120] or "podcast_audio")


def extension_from_url(url: str, default: str = ".mp3") -> str:
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    return suffix if suffix else default


def pick_audio_from_feed(xml_data: bytes) -> tuple[str, str] | None:
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return None

    channel = root.find("channel")
    if channel is not None:
        for item in channel.findall("item"):
            enclosure = item.find("enclosure")
            if enclosure is None:
                continue
            audio_url = enclosure.attrib.get("url", "").strip()
            if not audio_url:
                continue
            title = (item.findtext("title") or "podcast_episode").strip()
            return audio_url, title

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", default="podcast_episode", namespaces=ns) or "podcast_episode").strip()
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("rel") == "enclosure":
                audio_url = (link.attrib.get("href") or "").strip()
                if audio_url:
                    return audio_url, title
    return None


def download_to_file(url: str, output_dir: Path, suggested_name: str = "") -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        ext = extension_from_url(url)
        base = safe_filename(suggested_name) if suggested_name else safe_filename(Path(urlparse(url).path).stem)
        out_path = output_dir / f"{base}{ext}"
        with open(out_path, "wb") as f:
            while True:
                chunk = resp.read(1024 * 256)
                if not chunk:
                    break
                f.write(chunk)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Download podcast audio from an RSS feed URL or direct audio URL.")
    parser.add_argument("--url", required=True, help="RSS feed URL or direct audio URL")
    parser.add_argument("--output-dir", default="downloads", help="Download directory")
    args = parser.parse_args()

    url = args.url.strip()
    output_dir = Path(args.output_dir)

    lower = url.lower()
    if lower.endswith((".mp3", ".m4a", ".wav", ".aac", ".ogg")):
        out = download_to_file(url, output_dir)
        print(f"[ok] downloaded: {out}")
        return 0

    try:
        data, content_type = fetch_bytes(url)
    except Exception as e:
        print(f"[error] failed to fetch URL: {e}")
        return 1

    # Direct audio URL without extension
    if "audio/" in content_type:
        ext = ".mp3"
        if "mpeg" in content_type:
            ext = ".mp3"
        elif "mp4" in content_type or "m4a" in content_type:
            ext = ".m4a"
        elif "wav" in content_type:
            ext = ".wav"
        output_dir.mkdir(parents=True, exist_ok=True)
        base = safe_filename(Path(urlparse(url).path).stem)
        out = output_dir / f"{base}{ext}"
        out.write_bytes(data)
        print(f"[ok] downloaded: {out}")
        return 0

    picked = pick_audio_from_feed(data)
    if picked is None:
        print("[error] URL is not a supported RSS/Atom feed and not a direct audio URL")
        return 1

    audio_url, title = picked
    try:
        out = download_to_file(audio_url, output_dir, suggested_name=title)
    except Exception as e:
        print(f"[error] failed to download audio from feed: {e}")
        return 1
    print(f"[ok] feed latest episode: {title}")
    print(f"[ok] downloaded: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

