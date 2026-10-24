#!/usr/bin/env python3
"""Download verified open-access source PDFs for private literature retrieval.

Run from any directory:
    python 影视化配乐/理论参考/download_open_access.py

Only official author/publisher URLs are used. Commercial books are not downloaded.
The target directory is excluded from Git via the adjacent .gitignore.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "papers"

SOURCES = (
    {
        "filename": "Putkinen_2024_Bodily_Maps_of_Musical_Sensations.pdf",
        "url": "https://emotion.utu.fi/wp-content/uploads/2023/02/Putkinen_et_al_23.pdf",
        "doi": "10.1073/pnas.2308859121",
        "rights": "CC BY 4.0 (PNAS 2024); original authors credited",
    },
    {
        "filename": "Tsai_2026_Music_Emotion_Active_Interoceptive_Inference.pdf",
        "url": "https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1759699/pdf",
        "doi": "10.3389/fpsyg.2026.1759699",
        "rights": "CC BY (Frontiers 2026); original author credited",
    },
)


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    report = {
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "papers": [],
    }
    for item in SOURCES:
        path = DEST / item["filename"]
        state = "already_present" if path.exists() and path.stat().st_size > 1000 else None
        error = None
        if state is None:
            try:
                req = Request(item["url"], headers={"User-Agent": "Mozilla/5.0 (literature research)"})
                with urlopen(req, timeout=45) as response:
                    data = response.read()
                if not data.startswith(b"%PDF") or len(data) < 5_000:
                    raise ValueError("Downloaded response is not a valid-sized PDF")
                path.write_bytes(data)
                state = "downloaded"
            except (HTTPError, URLError, TimeoutError, ValueError) as exc:
                state = "failed"
                error = str(exc)
        result = dict(item)
        result["status"] = state
        if state != "failed":
            data = path.read_bytes()
            if not data.startswith(b"%PDF"):
                result["status"] = "invalid_existing_file"
                error = "File is not a PDF"
            else:
                result["sha256"] = hashlib.sha256(data).hexdigest()
                result["size_bytes"] = len(data)
                result["local_file"] = str(path)
        if error:
            result["error"] = error
        report["papers"].append(result)
        print(f'{item["filename"]}: {result["status"]}')
        if error:
            print(f"  {error}")
    (DEST / "download_manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    failed = [r for r in report["papers"] if r["status"] not in {"downloaded", "already_present"}]
    if failed:
        print("Some downloads failed; use official links in README.md to download them manually.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
