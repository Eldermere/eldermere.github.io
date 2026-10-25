#!/usr/bin/env python3
"""Build index.html and wiki.html from src/ by inlining the map, icons, saga text and Persian translations."""
import base64, json, re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
ICONS = ROOT.parent / "apps/desktop/assets/icons"
SITE_URL = "index.html"
WIKI_URL = "wiki.html"
RELEASE = ROOT / "release"
# Where the site serves release/ from. Relative works when release/ is deployed next to index.html;
# point it at a CDN or file host if the binaries live elsewhere.
DOWNLOAD_BASE = "release/"


def uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def releases():
    """One entry per launcher build in release/, tagged with the OS it runs on."""
    out = []
    for f in sorted(RELEASE.iterdir()) if RELEASE.is_dir() else []:
        name = f.name.lower()
        os_ = "windows" if name.endswith(".exe") else "mac" if any(k in name for k in ("apple", "mac", "darwin")) else "linux" if "linux" in name else None
        if f.is_file() and os_:
            out.append({"os": os_, "file": f.name, "size": f.stat().st_size})
    return out


def saga_chapters(name):
    src = (SRC / name).read_text()
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
    page = page.replace("{{RELEASES_JSON}}", json.dumps(releases())).replace("{{DOWNLOAD_BASE}}", DOWNLOAD_BASE)
    icons = {"compass": "compass", "totem": "totem_of_undying", "sword": "diamond_sword", "map": "filled_map",
             "bell": "bell", "emerald": "emerald", "spyglass": "spyglass"}
    for key, name in icons.items():
        page = page.replace("{{I_%s}}" % key, uri(ICONS / f"minecraft_{name}.png", "image/png"))
    (ROOT / "index.html").write_text(page)

    wiki = (SRC / "wiki.tpl.html").read_text().replace("{{BG}}", bg).replace("{{SITE}}", SITE_URL)
    saga = {"en": saga_chapters("saga.tpl.html"), "fa": saga_chapters("saga.fa.html")}
    wiki = wiki.replace("{{SAGA_JSON}}", json.dumps(saga, ensure_ascii=False).replace("</", "<\\/"))
    wiki = wiki.replace("{{WIKI_FA}}", (SRC / "wiki.fa.js").read_text().replace("</", "<\\/"))
    (ROOT / "wiki.html").write_text(wiki)
    print("Built index.html and wiki.html")


if __name__ == "__main__":
    main()
