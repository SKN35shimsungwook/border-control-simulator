"""AI 이미지(선택). secrets/환경변수에 키가 있을 때만 동작하고, 없거나 실패하면 SVG를 쓴다.

- POLLINATIONS_API_KEY : https://gen.pollinations.ai (flux)
- OPENAI_API_KEY       : OpenAI Images API (OPENAI_IMAGE_MODEL, 기본 gpt-image-1)

이미지는 서버에서 백그라운드 스레드로 미리 받아 두므로 키가 브라우저에 노출되지 않는다.
"""

import base64
import json
import os
import urllib.parse
import urllib.request
from concurrent.futures import Future, ThreadPoolExecutor

import streamlit as st

from . import data as D
from .models import Passport, Person

TIMEOUT = 90
MAX_ENTRIES = 120


def _secret(name: str) -> str | None:
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:  # secrets.toml 이 없으면 예외
        pass
    return os.environ.get(name)


def provider() -> str | None:
    if _secret("POLLINATIONS_API_KEY"):
        return "pollinations"
    if _secret("OPENAI_API_KEY"):
        return "openai"
    return None


@st.cache_resource
def _store() -> dict:
    return {"pool": ThreadPoolExecutor(max_workers=4), "jobs": {}}


def _fetch_pollinations(prompt: str, seed: int, w: int, h: int) -> bytes:
    q = urllib.parse.urlencode({"model": "flux", "width": w, "height": h, "seed": seed, "nologo": "true"})
    url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(prompt)}?{q}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {_secret('POLLINATIONS_API_KEY')}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        if not r.headers.get("Content-Type", "").startswith("image/"):
            raise RuntimeError("not an image")
        return r.read()


def _fetch_openai(prompt: str, seed: int, w: int, h: int) -> bytes:
    size = "1024x1536" if h > w else "1024x1024"
    body = json.dumps({
        "model": _secret("OPENAI_IMAGE_MODEL") or "gpt-image-1",
        "prompt": prompt,
        "size": size,
        "quality": "low",
        "n": 1,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={"Authorization": f"Bearer {_secret('OPENAI_API_KEY')}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return base64.b64decode(json.load(r)["data"][0]["b64_json"])


def request(key: str, prompt: str, seed: int, w: int, h: int) -> Future | None:
    prov = provider()
    if prov is None:
        return None
    store = _store()
    jobs: dict = store["jobs"]
    if key not in jobs:
        if len(jobs) >= MAX_ENTRIES:
            for old in list(jobs)[: MAX_ENTRIES // 2]:
                jobs.pop(old, None)
        fn = _fetch_pollinations if prov == "pollinations" else _fetch_openai
        jobs[key] = store["pool"].submit(fn, prompt, seed, w, h)
    return jobs[key]


def result(fut: Future | None) -> bytes | None | str:
    """bytes=완료, None=진행 중, "failed"=실패."""
    if fut is None or not fut.done():
        return None
    return "failed" if fut.exception() else fut.result()


# ---------- 프롬프트 ----------
def _sex(s: str) -> str:
    return "man" if s == "M" else "woman"


def _face_words(p: Person) -> str:
    f = p.face
    words = [f"{D.FACE_SHAPES[f.shape]} face", D.NOSES[f.nose], D.LIPS[f.lips], D.BROWS[f.brows], D.EYE_SIZES[f.eye_size]]
    if f.freckles:
        words.append("freckles")
    if f.dimples:
        words.append("dimples")
    r, g, b = (int(p.skin[i : i + 2], 16) for i in (1, 3, 5))
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    tones = [(200, "very light"), (170, "light"), (140, "medium"), (110, "tan"), (80, "brown")]
    words.append(next((t for cut, t in tones if lum >= cut), "deep brown") + " skin tone")
    return ", ".join(w for w in words if w)


def body_prompt(p: Person) -> str:
    parts = [
        f"full body photo of a {p.age}-year-old {_sex(p.sex)} traveler standing at an airport border control booth",
        f"{D.HAIR_COLORS[p.hair_color][0]} {D.HAIR_STYLES[p.hair_style][1]} hair",
        f"{D.EYE_COLORS[p.eye][0]} eyes",
        _face_words(p),
        f"wearing a {D.CLOTH_COLORS[p.top_color][0]} {D.TOPS[p.top][0]} and {D.CLOTH_COLORS[p.bottom_color][0]} {D.BOTTOMS[p.bottom][0]}",
        f"pulling a {D.LUGGAGE_COLORS[p.luggage_color][0]} suitcase",
    ]
    if p.glasses:
        parts.append("wearing glasses")
    if p.beard:
        parts.append("with a beard")
    if p.mark:
        parts.append(D.VISIBLE_MARKS[p.mark])
    if p.hat:
        parts.append(f"wearing a {D.HATS[p.hat]}")
    if p.bulge:
        parts.append("a noticeable bulge under the jacket")
    if p.nervous:
        parts.append("nervous sweating expression")
    parts.append("realistic, neutral lighting, detailed")
    return ", ".join(parts)


def portrait_prompt(pp: Passport, p: Person) -> str:
    parts = [
        f"passport ID photo, head and shoulders of a {p.age}-year-old {_sex(pp.sex)}",
        f"{D.HAIR_COLORS[pp.hair_color][0]} {D.HAIR_STYLES[p.hair_style][1]} hair",
        f"{D.EYE_COLORS[pp.eye][0]} eyes",
        _face_words(p),
        "plain light grey background, front facing, neutral expression",
    ]
    if pp.glasses:
        parts.append("wearing glasses")
    if pp.beard and pp.sex == "M":
        parts.append("with a beard")
    if pp.mark:
        parts.append(D.VISIBLE_MARKS[pp.mark])
    return ", ".join(parts)
