#!/usr/bin/env bash
# build.sh — build the dual-language install zips for release.
# Usage: ./build.sh <version-tag>   e.g. ./build.sh v1.2.0
#
# Produces in dist/:
#   visual-presentation-generator-zh.zip  (Simplified Chinese full package)
#   visual-presentation-generator-en.zip  (English-only; SKILL/README 0 CJK)
#   visual-presentation-generator.zip     (generic = current en)
# Logs sha256 for the Release upload. dist/*.zip is git-ignored.
set -euo pipefail
cd "$(dirname "$0")"
VERSION="${1:?usage: build.sh <version> eg v1.2.0}"
rm -rf dist && mkdir -p dist
python3 - "$VERSION" <<'PYEOF'
import hashlib, os, shutil, sys, zipfile

NAME = "visual-presentation-generator"
VERSION = sys.argv[1]
DOCS = ["SKILL.md", "README.md", "references/contracts.md", "references/validation.md",
        "references/schema.md", "references/NOTICE-garden-skills.md", "agents/openai.yaml"]
FORBID = {".git", "node_modules", "__pycache__", ".venv", ".env", "dist"}


def cjk_count(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def build_lang(lang, outzip):
    src = f"visual-presentation-generator-{lang}"
    assert os.path.isdir(src), f"missing source {src}"
    with zipfile.ZipFile(outzip, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src):
            dirs[:] = [d for d in dirs if d not in FORBID]
            rel = os.path.relpath(root, src).replace("\\", "/")
            for f in files:
                full = (rel + "/" + f).lstrip("/")
                if any(x in full.split("/") for x in FORBID):
                    continue
                z.write(os.path.join(root, f), f"{NAME}/{full}")
    with zipfile.ZipFile(outzip) as z:
        docs_text = ""
        for d in DOCS:
            try:
                docs_text += z.read(f"{NAME}/" + d).decode(errors="replace")
            except KeyError:
                pass
    n = cjk_count(docs_text)
    if lang == "en":
        assert n == 0, f"en SKILL/README still has {n} CJK chars"
    else:
        assert n > 100, f"zh SKILL/README has only {n} CJK chars"
    h = hashlib.sha256()
    with open(outzip, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    print(f"[{lang}] cjk_total={n} sha256={h.hexdigest()[:16]}… {outzip}")


build_lang("en", "dist/visual-presentation-generator-en.zip")
build_lang("zh", "dist/visual-presentation-generator-zh.zip")
shutil.copyfile("dist/visual-presentation-generator-en.zip",
                "dist/visual-presentation-generator.zip")
print("DONE; generic zip mirrors -en (current latest)")
PYEOF