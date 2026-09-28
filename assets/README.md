# 캐릭터 파츠 (선택)

게임은 기본적으로 코드로 그린 SVG 캐릭터를 씁니다. 이 폴더에 PNG 파츠를 넣으면 해당 부위만 PNG로 바뀝니다.

```
assets/parts/face/oval.png       얼굴 바탕(귀 포함) — oval, round, square, long, heart
assets/parts/hair/bob.png        머리카락 — short, sidepart, long, bob, curly, shaved, ponytail, bun, balding
assets/parts/top/coat.png        상의(팔 포함) — coat, hoodie, jacket, tee
assets/parts/bottom/long.png     하의+신발 — long, short
```

## 만드는 법

1. `python tools/make_part_guides.py` 를 실행하면 `assets/part_guides/` 에 정렬 가이드가 생깁니다 (크기·기준선 포함).
2. 가이드 크기에 맞춰 파츠를 그리거나 렌더링합니다.
   - **MakeHuman**(결과물 CC0)으로 얼굴·체형 슬라이더를 조절해 새 인물을 만들고 Blender에서 정면 렌더링하는 방식을 추천합니다.
   - 실존 인물 사진을 3D로 변환하거나 특정 인물을 닮게 만들지 않습니다. 사진은 얼굴 구조나 헤어스타일 같은 일반적인 특징을 참고하는 용도로만 씁니다.
3. **회색조**(밝은 회색 기준)로 저장하면 게임이 피부색·머리색·옷색을 입힙니다. 색을 그대로 쓰려면 `oval_raw.png` 처럼 `_raw` 를 붙입니다.
4. 얼굴 PNG에는 **눈·흉터·문신을 그리지 않습니다.** 눈동자 색·특이사항은 판정 근거라서 항상 SVG로 위에 그립니다. 코·입·눈썹도 SVG가 그립니다.
5. 앱을 재시작하면 반영됩니다. 앱의 **입국자 갤러리** 메뉴에서 결과를 한 번에 확인할 수 있습니다.
