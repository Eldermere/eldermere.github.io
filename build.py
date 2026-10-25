#!/usr/bin/env python3
"""Build index.html and wiki.html from src/ by inlining the map, icons and saga text."""
import base64, json, re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
ICONS = ROOT.parent / "apps/desktop/assets/icons"
SITE_URL = "https://claude.ai/artifact/BKjfRFs4Hx2i41mUWRDgb9"
WIKI_URL = "https://claude.ai/artifact/K3DjjgRhtuQ1izq9wCHZrK"


def uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def saga_chapters():
    src = (SRC / "saga.tpl.html").read_text()
    chapters = []
    for m in re.finditer(r'<article class="chapter" id="([^"]+)" data-label="([^"]+)"[^>]*>(.*?)</article>', src, re.S):
        body = m.group(3)
        num = re.search(r'<p class="num">(.*?)</p>', body).group(1)
        prose = re.search(r'<div class="prose">(.*)</div>\s*$', body, re.S).group(1).strip()
        chapters.append({"num": num, "label": m.group(2), "html": prose})
    return chapters


def main():
    bg = uri(SRC / "map.jpg", "image/jpeg")

    page = (SRC / "index.tpl.html").read_text().replace("{{BG}}", bg).replace("{{BOOK}}", WIKI_URL)
    icons = {"compass": "compass", "totem": "totem_of_undying", "sword": "diamond_sword", "map": "filled_map",
             "bell": "bell", "emerald": "emerald", "spyglass": "spyglass"}
    for key, name in icons.items():
        page = page.replace("{{I_%s}}" % key, uri(ICONS / f"minecraft_{name}.png", "image/png"))
    (ROOT / "index.html").write_text(page)

    wiki = (SRC / "wiki.tpl.html").read_text().replace("{{BG}}", bg).replace("{{SITE}}", SITE_URL)
    wiki = wiki.replace("{{SAGA_JSON}}", json.dumps(saga_chapters()).replace("</", "<\\/"))
    (ROOT / "wiki.html").write_text(wiki)
    print("Built index.html and wiki.html")


if __name__ == "__main__":
    main()
