#!/usr/bin/env python3
"""Generate 3 editorial photos for the landing page via OpenRouter + Gemini.

Each prompt evokes one of MCP / Skill / Plugin metaphorically with
National-Geographic-style photographic language: real materials, warm light,
shallow depth of field, no text/UI.
"""
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "google/gemini-3-pro-image-preview"
OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)

PROMPTS = {
    "mcp": (
        "Editorial photograph in the style of National Geographic: a craftsman's "
        "unfurled leather tool roll on a weathered oak workbench, brass and steel "
        "precision instruments arranged in slots — calipers, small wrenches, a "
        "magnifier, brass dividers. Warm tungsten side-light from the left, deep "
        "soft shadows, very shallow depth of field, slight grain, hyperreal "
        "textures. No text, no labels, no watermark. 16:9 horizontal."
    ),
    "skill": (
        "Editorial photograph in the style of National Geographic: an open vintage "
        "leather-bound field notebook on cream paper, neat handwritten notes and a "
        "small ink sketch, a brass fountain pen resting on the page, an old folded "
        "linen map peeking from underneath. Warm afternoon window light, faint "
        "dust motes, shallow depth of field, professional editorial composition. "
        "No text legible, no logos. 16:9 horizontal."
    ),
    "plugin": (
        "Editorial photograph in the style of National Geographic: a stack of three "
        "weathered hardwood field cases with brass corner fittings and leather "
        "straps, slightly opened to suggest contents, set on a stone surface in "
        "warm golden-hour light. Patina, scuffs, character. Background slightly "
        "out of focus, shallow depth of field, hyperreal textures. No text, no "
        "stickers, no labels. 16:9 horizontal."
    ),
}


def gen(name: str, prompt: str) -> Path | None:
    body = {
        "model": MODEL,
        "modalities": ["image", "text"],
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nichtagentur.github.io/cc-extensions/",
            "X-Title": "cc-extensions image gen",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read())
    msg = data["choices"][0]["message"]
    images = msg.get("images") or []
    if not images:
        print(f"[{name}] no image returned. payload keys: {list(msg.keys())}")
        print(json.dumps(msg, indent=2)[:600])
        return None
    url = images[0]["image_url"]["url"]
    if url.startswith("data:"):
        head, b64 = url.split(",", 1)
        ext = "png" if "png" in head else ("jpg" if "jpeg" in head else "img")
        out = OUT / f"{name}.{ext}"
        out.write_bytes(base64.b64decode(b64))
    else:
        ext = "jpg" if url.lower().endswith(("jpg", "jpeg")) else "png"
        out = OUT / f"{name}.{ext}"
        with urllib.request.urlopen(url, timeout=120) as r2:
            out.write_bytes(r2.read())
    print(f"[{name}] saved {out}  ({out.stat().st_size//1024} KB)")
    return out


if __name__ == "__main__":
    names = sys.argv[1:] or list(PROMPTS)
    for n in names:
        gen(n, PROMPTS[n])
