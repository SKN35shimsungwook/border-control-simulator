"""PNG 파츠 제작용 정렬 가이드 생성.  python tools/make_part_guides.py

assets/part_guides/<레이어>.png 를 만든다. 이 위에 레이어를 얹어 그리고(또는 Blender 렌더를 맞추고)
가이드 선을 지운 뒤 assets/parts/<레이어>/<변형>.png 로 저장하면 된다.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.parts import BOXES, PARTS_DIR, VARIANTS  # noqa: E402

SCALE = 10  # 도안 1단위 = 10px
OUT = PARTS_DIR.parent / "part_guides"

# 레이어별 기준선 (기본 폰트가 한글을 못 그려서 영어 라벨): (이름, 'h' 가로선 y / 'v' 세로선 x, 도안 좌표)
REFERENCE = {
    "face": [("eyes", "h", 29), ("nose tip", "h", 38), ("mouth", "h", 45), ("chin (oval)", "h", 59), ("ear (oval)", "v", -24), ("ear", "v", 24), ("center", "v", 0)],
    "hair": [("crown", "h", 2), ("eyes", "h", 29), ("chin", "h", 59), ("shoulder", "h", 64), ("center", "v", 0)],
    "top": [("shoulder", "h", 64), ("wrist", "h", 180), ("waist", "h", 190), ("coat hem", "h", 250), ("torso", "v", -38), ("torso", "v", 38)],
    "bottom": [("waist", "h", 190), ("shorts hem", "h", 250), ("sole", "h", 360), ("center", "v", 0)],
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for layer, (bx, by, bw, bh) in BOXES.items():
        img = Image.new("RGBA", (bw * SCALE, bh * SCALE), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, img.width - 1, img.height - 1], outline=(255, 0, 255, 255), width=3)
        for label, kind, v in REFERENCE[layer]:
            if kind == "h":
                y = (v - by) * SCALE
                d.line([0, y, img.width, y], fill=(0, 200, 255, 200), width=2)
                d.text((6, y + 4), label, fill=(0, 200, 255, 255))
            else:
                x = (v - bx) * SCALE
                d.line([x, 0, x, img.height], fill=(255, 200, 0, 200), width=2)
                d.text((x + 4, 6), label, fill=(255, 200, 0, 255))
        path = OUT / f"{layer}.png"
        img.save(path)
        print(f"{path.name}: {img.width}x{img.height}  variants: {', '.join(VARIANTS[layer])}")
        (PARTS_DIR / layer).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
