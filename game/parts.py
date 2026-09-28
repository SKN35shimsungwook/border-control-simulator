"""선택형 PNG 파츠 레이어.

assets/parts/<레이어>/<변형>.png 가 있으면 SVG 도형 대신 그 이미지를 쓴다.
예) assets/parts/face/oval.png, assets/parts/hair/bob.png, assets/parts/top/coat.png

- 파츠는 회색조(밝은 회색 기준)로 그려 두면 게임이 피부색·머리색·옷색을 곱하기(multiply)로 입힌다.
  색을 그대로 쓰고 싶으면 파일명 끝에 `_raw` 를 붙인다 (예: face/oval_raw.png).
- 이미지는 BOXES 의 영역(도안 좌표)에 꽉 차게 늘려 그린다. 가로세로 비율을 맞춰 10배 해상도로 만들면 좋다.
- 눈동자·흉터·문신처럼 판정에 쓰이는 특징은 항상 SVG로 위에 그려서 정확성을 지킨다.
- 파일을 추가한 뒤에는 앱을 재시작해야 반영된다.
"""

import base64
from functools import lru_cache
from pathlib import Path

PARTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "parts"

# 레이어 → (x, y, width, height) : 180cm 기준 인물 도안 좌표
BOXES = {
    "face": (-32, 0, 64, 68),  # 얼굴(귀 포함) 바탕. 눈·코·입은 SVG가 그림
    "hair": (-40, -16, 80, 112),  # 앞머리+뒷머리 전체
    "top": (-56, 60, 112, 194),  # 상의(팔 포함)
    "bottom": (-32, 186, 64, 172),  # 하의+신발
}

# 레이어별로 쓰는 변형 이름 (파일명)
VARIANTS = {
    "face": ["oval", "round", "square", "long", "heart"],
    "hair": ["short", "sidepart", "long", "bob", "curly", "shaved", "ponytail", "bun", "balding"],
    "top": ["coat", "hoodie", "jacket", "tee"],
    "bottom": ["long", "short"],
}


@lru_cache(maxsize=128)
def _load(layer: str, variant: str) -> tuple[str, bool] | None:
    for name, raw in ((f"{variant}_raw.png", True), (f"{variant}.png", False)):
        path = PARTS_DIR / layer / name
        if path.is_file():
            return base64.b64encode(path.read_bytes()).decode(), raw
    return None


def has(layer: str, variant: str) -> bool:
    return _load(layer, variant) is not None


def image(layer: str, variant: str, tint: str) -> str:
    """SVG <image> 조각. 파일이 없으면 빈 문자열."""
    found = _load(layer, variant)
    if not found:
        return ""
    b64, raw = found
    x, y, w, h = BOXES[layer]
    img = (
        f'<image href="data:image/png;base64,{b64}" x="{x}" y="{y}" width="{w}" height="{h}" '
        f'preserveAspectRatio="none"{{filter}}/>'
    )
    if raw:
        return img.format(filter="")
    fid = f"tint-{layer}-{variant}-{tint.lstrip('#')}"
    return (
        f'<defs><filter id="{fid}" color-interpolation-filters="sRGB">'
        f'<feFlood flood-color="{tint}"/><feComposite in2="SourceAlpha" operator="in"/>'
        f'<feBlend in2="SourceGraphic" mode="multiply"/></filter></defs>'
        + img.format(filter=f' filter="url(#{fid})"')
    )
