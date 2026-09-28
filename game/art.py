"""SVG 일러스트 생성: 심사대 인물, 여권 사진, 캐리어 X-ray, 금속탐지기, 몸수색."""

import base64
import random

from . import data as D
from . import parts
from .models import Face, Item, Passport, Person


def as_img(svg: str, max_width: str = "100%") -> str:
    """st.html 은 <svg> 를 걸러내므로 data URI 이미지로 감싼다."""
    b64 = base64.b64encode(svg.encode("utf-8")).decode()
    return f'<img src="data:image/svg+xml;base64,{b64}" style="width:100%;max-width:{max_width};height:auto;display:block"/>'


def _hair_hex(name: str) -> str:
    return D.HAIR_COLORS[name][1]


def _darker(hex_color: str, f: float = 0.75) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"#{int(r * f):02x}{int(g * f):02x}{int(b * f):02x}"


def _mix(a: str, b: str, t: float) -> str:
    ca = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def _lighter(hex_color: str, t: float = 0.25) -> str:
    return _mix(hex_color, "#ffffff", t)


def _radial(gid: str, base: str) -> str:
    """왼쪽 위에서 빛이 드는 입체 음영."""
    return (f'<defs><radialGradient id="{gid}" cx="38%" cy="32%" r="75%">'
            f'<stop offset="0" stop-color="{_lighter(base, 0.22)}"/><stop offset="0.6" stop-color="{base}"/>'
            f'<stop offset="1" stop-color="{_darker(base, 0.78)}"/></radialGradient></defs>')


def _linear(gid: str, base: str) -> str:
    """원기둥처럼 가운데가 밝고 가장자리가 어두운 음영 (몸통·팔·다리)."""
    return (f'<defs><linearGradient id="{gid}" x1="0" x2="1" y1="0" y2="0">'
            f'<stop offset="0" stop-color="{_darker(base, 0.72)}"/><stop offset="0.35" stop-color="{_lighter(base, 0.12)}"/>'
            f'<stop offset="0.7" stop-color="{base}"/><stop offset="1" stop-color="{_darker(base, 0.65)}"/></linearGradient></defs>')


# ---------- 머리(얼굴) : 중심 (0, 32), 기본 반폭 24 ----------
# 얼굴형 → (반폭, 턱 y)
SHAPE_GEOM = {"oval": (24, 59), "round": (26, 57), "square": (25, 59), "long": (21.5, 61), "heart": (25, 59)}
EYE_GEOM = {"small": (5, 3.2, 2.6), "normal": (6, 4, 3.2), "large": (7, 4.8, 3.8)}
BROW_WIDTH = {"thin": 1.5, "medium": 2.5, "thick": 3.8, "arched": 2.3}


def _face_path(shape: str, w: float, chin: float) -> str:
    if shape == "square":
        return f"M{-w},20 Q{-w},5 0,5 Q{w},5 {w},20 L{w},44 Q{w - 2},{chin - 1} 0,{chin} Q{-(w - 2)},{chin - 1} {-w},44 Z"
    if shape == "heart":
        return f"M{-w},22 Q{-w},5 0,5 Q{w},5 {w},22 Q{w - 1},44 0,{chin} Q{-(w - 1)},44 {-w},22 Z"
    cy, ry = (5 + chin) / 2, (chin - 5) / 2
    return f"M{-w},{cy} A{w},{ry} 0 1,1 {w},{cy} A{w},{ry} 0 1,1 {-w},{cy} Z"


def _hair_back(style: str, hair: str) -> str:
    if style == "long":
        return f'<path d="M-28,26 Q-31,85 -21,94 L21,94 Q31,85 28,26 Z" fill="{hair}"/>'
    if style == "bob":
        return f'<path d="M-29,24 Q-31,58 -25,63 L25,63 Q31,58 29,24 Z" fill="{hair}"/>'
    if style == "ponytail":
        return f'<ellipse cx="25" cy="44" rx="8" ry="22" fill="{hair}"/>'
    if style == "bun":
        return f'<circle cx="0" cy="-3" r="11" fill="{hair}"/>'
    if style == "curly":
        return "".join(f'<circle cx="{x}" cy="{y}" r="10" fill="{hair}"/>' for x, y in ((-27, 40), (27, 40), (-24, 52), (24, 52)))
    return ""


def _hair_front(style: str, hair: str) -> str:
    if style == "shaved":
        return f'<path d="M-24,26 Q-24,4 0,4 Q24,4 24,26 Q12,14 0,14 Q-12,14 -24,26 Z" fill="{hair}" opacity="0.45"/>'
    if style == "curly":
        return "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{hair}"/>'
                       for x, y in ((-20, 16), (-10, 8), (0, 5), (10, 8), (20, 16), (-26, 27), (26, 27)))
    if style == "sidepart":
        return (f'<path d="M-26,30 Q-28,2 2,2 Q28,4 26,28 Q24,14 12,12 Q-4,8 -9,11 Q-20,15 -26,30 Z" fill="{hair}"/>'
                f'<path d="M-9,4 L-9,11" stroke="{_darker(hair, 0.7)}" stroke-width="1.2"/>')
    if style == "bob":
        return f'<path d="M-27,30 Q-29,0 0,0 Q29,0 27,30 L23,18 Q0,13 -23,18 Z" fill="{hair}"/>'
    if style == "bun":
        return f'<path d="M-25,26 Q-26,3 0,3 Q26,3 25,26 Q16,11 0,11 Q-16,11 -25,26 Z" fill="{hair}"/>'
    if style == "balding":
        return (f'<path d="M-25,36 Q-27,18 -19,13 L-16,23 Q-20,27 -21,36 Z" fill="{hair}"/>'
                f'<path d="M25,36 Q27,18 19,13 L16,23 Q20,27 21,36 Z" fill="{hair}"/>'
                '<ellipse cx="-6" cy="10" rx="6" ry="3" fill="#ffffff" opacity="0.18"/>')
    return f'<path d="M-26,30 Q-28,2 0,2 Q28,2 26,30 Q20,14 4,15 Q-12,12 -26,30 Z" fill="{hair}"/>'


def _nose(kind: str, shade: str) -> str:
    line = f'stroke="{shade}" stroke-width="1.5" fill="none" stroke-linecap="round"'
    if kind == "small":
        return f'<path d="M1,32 Q-2,37 1,38" {line}/>'
    if kind == "wide":
        return (f'<path d="M-1,28 L-2,35" {line} opacity="0.6"/><path d="M-6,37 Q-4,40 0,39 Q4,40 6,37" {line}/>'
                f'<circle cx="-3" cy="38" r="0.9" fill="{shade}"/><circle cx="3" cy="38" r="0.9" fill="{shade}"/>')
    if kind == "hooked":
        return f'<path d="M-1,26 Q5,33 2,38 Q0,40 -3,38" {line}/>'
    if kind == "button":
        return f'<circle cx="0" cy="36" r="3" fill="{shade}" opacity="0.25"/><path d="M-3,38 Q0,40 3,38" {line}/>'
    return f'<path d="M0,26 L-2,36 Q0,39 3,38" {line}/>'


def _lips(kind: str, skin: str) -> str:
    lip = _mix(skin, "#b24a4a", 0.4)
    dark = _darker(lip, 0.7)
    if kind == "thin":
        return f'<path d="M-7,46 Q0,48 7,46" stroke="{dark}" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
    if kind == "full":
        return (f'<path d="M-9,45 Q-4,41.5 0,43 Q4,41.5 9,45 Q0,47 -9,45 Z" fill="{dark}"/>'
                f'<path d="M-9,45 Q0,53 9,45 Q0,47 -9,45 Z" fill="{lip}"/>')
    return (f'<path d="M-8,45 Q-3,43 0,44 Q3,43 8,45 Q0,46.5 -8,45 Z" fill="{dark}"/>'
            f'<path d="M-8,45 Q0,50.5 8,45 Q0,46.5 -8,45 Z" fill="{lip}"/>')


def _head(
    face: Face,
    skin: str,
    hair_color: str,
    hair_style: str,
    eye: str,
    glasses: bool,
    beard: bool,
    mark: str | None,
    age: int,
    hat: str | None = None,
    nervous: bool = False,
) -> str:
    """hair_style 은 그리기 키(short, bob ...)."""
    hair = _hair_hex(hair_color)
    iris = D.EYE_COLORS[eye][1]
    shade = _darker(skin, 0.72)
    w, chin = SHAPE_GEOM[face.shape]
    sx = w / 24
    s = []

    hair_png = parts.image("hair", hair_style, hair)
    if not hair_png:
        s.append(f'<g transform="scale({sx:.3f},1)">{_hair_back(hair_style, hair)}</g>')
    # 목
    s.append(f'<rect x="-8" y="50" width="16" height="18" fill="{skin}"/>')
    s.append(f'<rect x="-8" y="{chin - 2}" width="16" height="5" fill="{shade}" opacity="0.35"/>')
    # 얼굴 바탕 + 귀
    face_png = parts.image("face", face.shape, skin)
    if face_png:
        s.append(face_png)
    else:
        er = D.EARS[face.ears]
        gid = f"skin{skin[1:]}"
        s.append(_radial(gid, skin))
        s.append(f'<ellipse cx="{-w}" cy="34" rx="{er}" ry="{er * 1.5}" fill="{_darker(skin, 0.9)}"/>'
                 f'<ellipse cx="{w}" cy="34" rx="{er}" ry="{er * 1.5}" fill="{_darker(skin, 0.85)}"/>')
        s.append(f'<path d="{_face_path(face.shape, w, chin)}" fill="url(#{gid})"/>')
        # 코 옆 그림자·이마 하이라이트
        s.append(f'<ellipse cx="3" cy="35" rx="3" ry="5" fill="{shade}" opacity="0.18"/>'
                 f'<ellipse cx="-6" cy="14" rx="9" ry="4" fill="#ffffff" opacity="0.12"/>')
        s.append(f'<path d="M{-w + 3},44 Q0,{chin + 2} {w - 3},44" stroke="{shade}" stroke-width="3" fill="none" opacity="0.18"/>')
    # 볼 홍조
    blush = _mix(skin, "#d0605a", 0.5)
    s.append(f'<ellipse cx="{-w * 0.62:.1f}" cy="40" rx="5" ry="3" fill="{blush}" opacity="0.25"/>'
             f'<ellipse cx="{w * 0.62:.1f}" cy="40" rx="5" ry="3" fill="{blush}" opacity="0.25"/>')
    # 나이 주름
    wrinkle = f'stroke="{shade}" stroke-width="1" fill="none" opacity="0.7" stroke-linecap="round"'
    if age >= 45:
        s.append(f'<path d="M-9,14 Q0,12 9,14 M-7,17 Q0,15.5 7,17" {wrinkle}/>')
    if age >= 55:
        s.append(f'<path d="M-6,38 Q-10,43 -9,48 M6,38 Q10,43 9,48" {wrinkle}/>')
    if age >= 62:
        s.append(f'<path d="M-17,27 L-20,25 M-17,30 L-20,31 M17,27 L20,25 M17,30 L20,31" {wrinkle}/>')
    if face.freckles:
        dots = ((-14, 36), (-11, 38), (-16, 39), (-12, 35), (14, 36), (11, 38), (16, 39), (12, 35), (-2, 33), (2, 33))
        s.append("".join(f'<circle cx="{x}" cy="{y}" r="0.8" fill="{_darker(skin, 0.78)}"/>' for x, y in dots))
    # 앞머리
    if hair_png:
        s.append(hair_png)
    else:
        s.append(f'<g transform="scale({sx:.3f},1)">{_hair_front(hair_style, hair)}</g>')
        if hair_style not in ("shaved", "balding", "curly"):
            s.append(f'<path d="M-15,9 Q-5,3 9,5" stroke="#ffffff" stroke-width="3" fill="none" opacity="0.2" stroke-linecap="round"/>')
    # 눈썹 (초조하면 안쪽 끝이 올라감)
    inner = 17 if nervous else 20
    peak = 16 if face.brows == "arched" else 19
    brow_col = _darker(hair, 0.8) if hair_style in ("shaved", "balding") else hair
    s.append(f'<path d="M-16,22 Q-11,{peak} -5,{inner} M5,{inner} Q11,{peak} 16,22" stroke="{brow_col}" '
             f'stroke-width="{BROW_WIDTH[face.brows]}" fill="none" stroke-linecap="round"/>')
    # 눈
    rx, ry, ir = EYE_GEOM[face.eye_size]
    for x in (-10, 10):
        s.append(f'<ellipse cx="{x}" cy="29" rx="{rx}" ry="{ry}" fill="#fff"/>')
        s.append(f'<circle cx="{x}" cy="29" r="{ir}" fill="{iris}"/><circle cx="{x}" cy="29" r="{ir * 0.42:.2f}" fill="#111"/>')
        s.append(f'<circle cx="{x + 1}" cy="28" r="{ir * 0.25:.2f}" fill="#fff" opacity="0.8"/>')
        s.append(f'<path d="M{x - rx},29 Q{x},{29 - ry * 1.5:.1f} {x + rx},29" stroke="{_darker(skin, 0.45)}" stroke-width="1.3" fill="none"/>')
    # 코·입
    s.append(_nose(face.nose, shade))
    s.append(_lips(face.lips, skin))
    if face.dimples:
        s.append(f'<path d="M-11,44 q-1,2 0,4 M11,44 q1,2 0,4" {wrinkle}/>')
    if beard:
        s.append(f'<g transform="scale({sx:.3f},1)"><path d="M-22,36 Q-20,{chin + 3} 0,{chin + 3} Q20,{chin + 3} 22,36 '
                 f'Q16,50 8,48 Q0,51 -8,48 Q-16,50 -22,36 Z" fill="{hair}" opacity="0.92"/></g>')
    if glasses:
        s.append('<g fill="none" stroke="#222" stroke-width="1.8"><rect x="-18" y="23" width="15" height="12" rx="3"/>'
                 '<rect x="3" y="23" width="15" height="12" rx="3"/><path d="M-3,28 L3,28"/></g>')
    # 특이사항 (판정 근거이므로 항상 SVG로 그림)
    scar = 'stroke="#8b2e2e" stroke-width="2" stroke-linecap="round"'
    if mark == "왼쪽 뺨 흉터":
        s.append(f'<path d="M-17,34 L-9,45 M-16,38 L-13,37 M-13,42 L-10,40" {scar}/>')
    elif mark == "오른쪽 뺨 흉터":
        s.append(f'<path d="M17,34 L9,45 M16,38 L13,37 M13,42 L10,40" {scar}/>')
    elif mark == "눈썹 흉터":
        s.append(f'<path d="M8,15 L13,26" {scar}/>')
    elif mark == "턱 흉터":
        s.append(f'<path d="M-5,{chin - 5} L5,{chin - 7}" {scar}/>')
    elif mark == "코 옆 점":
        s.append('<circle cx="7" cy="37" r="2.2" fill="#3a2418"/>')
    elif mark == "목 장미 문신":
        s.append('<g transform="translate(-3,62)"><circle r="3.5" fill="#b3263b"/><circle r="1.5" fill="#6d1020"/>'
                 '<path d="M0,3 L0,8 M0,6 L3,5" stroke="#2f6b2f" stroke-width="1.5"/></g>')
    if nervous:
        s.append(f'<path d="M{w - 4},12 Q{w - 1},18 {w - 4},20 Q{w - 7},18 {w - 4},12 Z" fill="#7fc8ff"/>')
    # 모자
    hat_svg = ""
    if hat == "야구모자":
        hat_svg = '<path d="M-26,18 Q-26,-2 0,-2 Q26,-2 26,18 Z" fill="#35507a"/><path d="M-4,16 L40,18 L-4,21 Z" fill="#2a3f60"/>'
    elif hat == "비니":
        hat_svg = '<path d="M-26,20 Q-26,-8 0,-8 Q26,-8 26,20 Z" fill="#9c3d3d"/><rect x="-27" y="14" width="54" height="8" rx="3" fill="#7a2c2c"/>'
    elif hat == "페도라":
        hat_svg = ('<ellipse cx="0" cy="12" rx="38" ry="6" fill="#3b3024"/><path d="M-20,12 Q-18,-12 0,-10 Q18,-12 20,12 Z" fill="#4a3c2c"/>'
                   '<rect x="-20" y="6" width="40" height="5" fill="#231b12"/>')
    if hat_svg:
        s.append(f'<g transform="scale({sx:.3f},1)">{hat_svg}</g>')
    return "".join(s)


def person_svg(p: Person) -> str:
    """심사대 앞 인물 전신 + 키 눈금자 + 캐리어."""
    floor = 420
    scale = (p.height * 2) / 360  # 1cm = 2px, 기본 도안은 180cm
    top_hex = D.CLOTH_COLORS[p.top_color][1]
    bot_hex = D.CLOTH_COLORS[p.bottom_color][1]
    top_kind = D.TOPS[p.top][1]
    bot_kind = D.BOTTOMS[p.bottom][1]
    lug_hex = D.LUGGAGE_COLORS[p.luggage_color][1]

    ruler = ['<g font-size="9" fill="#9fb3c8" font-family="monospace">']
    for cm in range(100, 205, 5):
        y = floor - cm * 2
        w = 16 if cm % 10 == 0 else 9
        ruler.append(f'<line x1="18" x2="{18 + w}" y1="{y}" y2="{y}" stroke="#6c8199" stroke-width="1"/>')
        if cm % 10 == 0:
            ruler.append(f'<text x="38" y="{y + 3}">{cm}</text>')
    ruler.append("</g>")

    b = [_linear("gTop", top_hex), _linear("gBot", bot_hex), _linear("gSkin", p.skin)]
    bottom_png = parts.image("bottom", bot_kind, bot_hex)
    top_png = parts.image("top", top_kind, top_hex)
    # 다리
    if bottom_png:
        b.append(bottom_png)
    elif bot_kind == "short":
        b.append('<rect x="-28" y="190" width="24" height="60" fill="url(#gBot)"/><rect x="4" y="190" width="24" height="60" fill="url(#gBot)"/>')
        b.append('<rect x="-25" y="250" width="18" height="96" fill="url(#gSkin)"/><rect x="7" y="250" width="18" height="96" fill="url(#gSkin)"/>')
    else:
        b.append('<rect x="-28" y="190" width="24" height="156" fill="url(#gBot)"/><rect x="4" y="190" width="24" height="156" fill="url(#gBot)"/>')
    if not bottom_png:
        b.append('<ellipse cx="-16" cy="352" rx="17" ry="8" fill="#1d1d1d"/><ellipse cx="16" cy="352" rx="17" ry="8" fill="#1d1d1d"/>')
    # 몸통과 팔
    top_start = len(b)
    sleeve_end = 110 if top_kind == "tee" and p.top == "티셔츠" else 180
    for x in (-52, 38):
        b.append(f'<rect x="{x}" y="70" width="14" height="{sleeve_end - 70}" rx="6" fill="url(#gTop)"/>')
        if sleeve_end < 180:
            b.append(f'<rect x="{x + 1}" y="{sleeve_end}" width="12" height="{180 - sleeve_end}" rx="5" fill="url(#gSkin)"/>')
        b.append(f'<circle cx="{x + 7}" cy="188" r="8" fill="{p.skin}"/>')
    torso_bottom = 250 if top_kind == "coat" else 196
    b.append(f'<path d="M-38,72 Q-40,66 -30,64 L30,64 Q40,66 38,72 L36,{torso_bottom} L-36,{torso_bottom} Z" fill="url(#gTop)"/>')
    b.append(f'<path d="M-30,66 Q0,76 30,66 L30,74 Q0,82 -30,74 Z" fill="#000" opacity="0.12"/>')
    if top_kind == "coat":
        b.append(f'<path d="M0,66 L0,{torso_bottom}" stroke="{_darker(top_hex)}" stroke-width="2"/>')
        b.append(f'<path d="M-12,64 L0,90 L12,64" fill="{_darker(top_hex, 0.85)}"/>')
    elif top_kind == "hoodie":
        b.append(f'<path d="M-20,64 Q0,86 20,64" stroke="{_darker(top_hex)}" stroke-width="5" fill="none"/>')
        b.append(f'<rect x="-18" y="140" width="36" height="22" rx="4" fill="{_darker(top_hex, 0.88)}"/>')
    elif top_kind == "jacket":
        b.append('<path d="M-10,64 L0,120 L10,64 Z" fill="#f2f2f2"/>')
        b.append(f'<path d="M-14,64 L0,122 L14,64" stroke="{_darker(top_hex)}" stroke-width="3" fill="none"/>')
    else:
        b.append(f'<path d="M-10,64 Q0,74 10,64" stroke="{_darker(top_hex)}" stroke-width="2" fill="none"/>')
    if top_png:
        del b[top_start:]
        b.append(top_png)
    if p.bulge:
        b.append(f'<ellipse cx="14" cy="140" rx="15" ry="20" fill="{_darker(top_hex, 0.8)}" opacity="0.9"/>')
        b.append(f'<path d="M2,128 Q14,118 26,130" stroke="{_darker(top_hex, 0.6)}" stroke-width="1.5" fill="none"/>')
    if top_kind != "coat" and not top_png:
        b.append('<rect x="-36" y="186" width="72" height="7" fill="#3a2a1a"/><rect x="-5" y="185" width="10" height="9" fill="#c9b27a"/>')
    head = _head(p.face, p.skin, p.hair_color, D.HAIR_STYLES[p.hair_style][0], p.eye, p.glasses, p.beard, p.mark,
                 p.age, p.hat, p.nervous)

    feet_y = floor - 4
    shadow = (f'<ellipse cx="140" cy="{floor - 1}" rx="{46 * scale:.1f}" ry="6" fill="#000" opacity="0.35"/>'
              f'<ellipse cx="248" cy="{floor - 1}" rx="30" ry="4" fill="#000" opacity="0.3"/>')
    person_g = (
        f'<g transform="translate(140,{feet_y}) scale({scale:.3f}) translate(0,-360)">'
        f'{"".join(b)}<g>{head}</g></g>'
    )
    suitcase = (
        f'<g transform="translate(222,{floor - 118})">'
        f'<rect x="12" y="-26" width="6" height="30" fill="#555"/><rect x="30" y="-26" width="6" height="30" fill="#555"/>'
        f'<rect x="8" y="-30" width="32" height="7" rx="3" fill="#444"/>'
        f'<rect x="0" y="0" width="48" height="110" rx="8" fill="{lug_hex}" stroke="{_darker(lug_hex, 0.6)}" stroke-width="2"/>'
        f'<path d="M12,8 L12,102 M36,8 L36,102" stroke="{_darker(lug_hex, 0.8)}" stroke-width="3"/>'
        f'<circle cx="8" cy="114" r="5" fill="#222"/><circle cx="40" cy="114" r="5" fill="#222"/></g>'
    )
    return (
        f'<svg viewBox="0 0 300 440" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto">'
        '<defs><linearGradient id="wall" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#1c2a3a"/>'
        '<stop offset="1" stop-color="#2b3d52"/></linearGradient></defs>'
        '<rect width="300" height="440" fill="url(#wall)"/>'
        f'<rect y="{floor}" width="300" height="20" fill="#3a3a3a"/>'
        f'{"".join(ruler)}{shadow}{person_g}{suitcase}</svg>'
    )


def passport_photo_svg(pp: Passport, p: Person) -> str:
    """여권 사진은 여권에 적힌 특징(눈동자, 특이사항, 성별, 머리색 등)으로 그린다."""
    face, style = p.face, D.HAIR_STYLES[p.hair_style][0]
    if pp.sex != p.sex:  # 성별이 다른 여권 → 다른 사람 사진처럼 보이게
        style = "long" if pp.sex == "F" else "short"
        shapes, noses = list(D.FACE_SHAPES), list(D.NOSES)
        face = Face(
            shape=shapes[(shapes.index(face.shape) + 2) % len(shapes)],
            nose=noses[(noses.index(face.nose) + 2) % len(noses)],
            lips="full" if face.lips == "thin" else "thin",
            brows=face.brows,
            eye_size=face.eye_size,
            ears=face.ears,
        )
    head = _head(face, p.skin, pp.hair_color, style, pp.eye, pp.glasses, pp.beard and pp.sex == "M", pp.mark, p.age)
    shoulders = '<path d="M-44,96 Q-40,70 -10,66 L10,66 Q40,70 44,96 Z" fill="#4a5568"/>'
    return (
        '<svg viewBox="0 0 100 124" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="100" height="124" fill="#dfe7ee"/>'
        f'<g transform="translate(50,14) scale(1.25)">{shoulders}{head}</g>'
        '<rect width="100" height="124" fill="#7aa0c4" opacity="0.12"/></svg>'
    )


# ---------- X-ray ----------
ORG = "#e8983a"  # 유기물
MET = "#3f7fe0"  # 금속
MIX = "#4fbf7a"  # 혼합
DENSE = "#23408f"


def _xray_shape(kind: str) -> str:
    """중심 (0,0), 대략 80x90 크기 안에 그린다."""
    if kind == "clothes":
        return (f'<rect x="-36" y="-26" width="72" height="52" rx="10" fill="{ORG}" opacity="0.35"/>'
                f'<path d="M-30,-8 L30,-8 M-30,8 L30,8" stroke="{ORG}" stroke-width="2" opacity="0.6"/>')
    if kind == "shoes":
        return (f'<path d="M-34,-10 Q-34,-26 -18,-24 L-6,-10 Q2,-4 2,4 L-34,4 Z" fill="{ORG}" opacity="0.6"/>'
                f'<path d="M-2,14 Q-2,-2 14,0 L26,14 Q34,20 34,28 L-2,28 Z" fill="{ORG}" opacity="0.6"/>')
    if kind == "laptop":
        return (f'<rect x="-38" y="-24" width="76" height="48" rx="4" fill="{MIX}" opacity="0.65"/>'
                f'<rect x="-30" y="-16" width="30" height="20" fill="{MET}" opacity="0.7"/><rect x="10" y="4" width="22" height="14" fill="{MET}" opacity="0.8"/>')
    if kind == "toiletry":
        return (f'<rect x="-28" y="-20" width="16" height="42" rx="5" fill="{ORG}" opacity="0.7"/>'
                f'<rect x="-6" y="-12" width="14" height="34" rx="4" fill="{ORG}" opacity="0.55"/>'
                f'<rect x="14" y="-4" width="18" height="26" rx="3" fill="{MIX}" opacity="0.6"/>')
    if kind == "book":
        return "".join(f'<rect x="-30" y="{y}" width="60" height="12" fill="{ORG}" opacity="0.55" stroke="{ORG}"/>' for y in (-20, -6, 8))
    if kind == "camera":
        return (f'<rect x="-28" y="-18" width="56" height="36" rx="5" fill="{MET}" opacity="0.75"/>'
                f'<circle r="12" fill="{DENSE}"/><circle r="6" fill="{MIX}"/>')
    if kind == "charger":
        return (f'<rect x="-10" y="-10" width="20" height="20" fill="{MIX}"/>'
                f'<path d="M10,0 Q30,-20 20,10 Q10,30 -20,20 Q-40,10 -30,-10" stroke="{MET}" stroke-width="2.5" fill="none"/>')
    if kind == "umbrella":
        return (f'<path d="M-38,20 L30,-20" stroke="{MET}" stroke-width="3"/>'
                f'<path d="M-24,4 L22,-24 L30,-10 Z" fill="{ORG}" opacity="0.4"/><path d="M-38,20 q-6,6 0,10" stroke="{MET}" stroke-width="3" fill="none"/>')
    if kind == "bottle":
        return f'<path d="M-6,-32 L6,-32 L6,-20 Q16,-14 16,0 L16,30 L-16,30 L-16,0 Q-16,-14 -6,-20 Z" fill="{ORG}" opacity="0.6"/>'
    if kind == "doll":
        return (f'<circle cy="-16" r="14" fill="{ORG}" opacity="0.5"/><ellipse cy="14" rx="20" ry="20" fill="{ORG}" opacity="0.5"/>'
                f'<circle cx="-5" cy="-18" r="2" fill="{MET}"/><circle cx="5" cy="-18" r="2" fill="{MET}"/>')
    if kind == "pistol":
        return (f'<path d="M-34,-14 L30,-14 L30,-2 L-6,-2 L-2,4 L-8,26 L-22,26 L-18,-2 L-34,-2 Z" fill="{DENSE}"/>'
                f'<circle cx="-6" cy="6" r="4" fill="none" stroke="{DENSE}" stroke-width="2"/>')
    if kind == "knife":
        return (f'<path d="M-36,4 L-6,4 L-6,-4 L-36,-4 Z" fill="{ORG}" opacity="0.8"/>'
                f'<path d="M-6,-6 L34,-2 Q38,0 34,4 L-6,6 Z" fill="{DENSE}"/>')
    if kind == "ammo":
        return "".join(f'<rect x="{x}" y="-14" width="7" height="24" rx="3" fill="{DENSE}"/>' for x in range(-30, 32, 10))
    if kind == "drug":
        return "".join(
            f'<g transform="translate({x},{y})"><rect x="-17" y="-11" width="34" height="22" fill="#c46a1f"/>'
            f'<path d="M-17,-11 L17,11 M17,-11 L-17,11" stroke="#8a4410" stroke-width="2"/></g>'
            for x, y in ((-18, -12), (18, -12), (-18, 14), (18, 14))
        )
    if kind == "bomb":
        tubes = "".join(f'<rect x="{x}" y="-22" width="13" height="44" rx="5" fill="{ORG}"/>' for x in (-34, -19, -4))
        return (f'{tubes}<rect x="14" y="-12" width="22" height="16" fill="{MIX}"/>'
                f'<path d="M-28,-22 Q0,-40 20,-12 M-12,22 Q10,36 30,4" stroke="{MET}" stroke-width="2.5" fill="none"/>')
    return f'<rect x="-20" y="-20" width="40" height="40" fill="{ORG}" opacity="0.4"/>'


def xray_svg(items: list[Item], seed: int) -> str:
    rng = random.Random(seed)
    cols, rows = 4, 2
    cells = [(c, r) for r in range(rows) for c in range(cols)]
    rng.shuffle(cells)
    parts = []
    for item, (c, r) in zip(items, cells):
        x = 70 + c * 95 + rng.randint(-8, 8)
        y = 90 + r * 110 + rng.randint(-8, 8)
        parts.append(f'<g transform="translate({x},{y}) rotate({rng.randint(-25, 25)})">{_xray_shape(item.kind)}</g>')
    return (
        '<svg viewBox="0 0 420 300" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto">'
        '<rect width="420" height="300" fill="#060d18"/>'
        '<rect x="18" y="28" width="384" height="250" rx="18" fill="none" stroke="#2b5fa8" stroke-width="5"/>'
        '<rect x="180" y="12" width="60" height="18" rx="6" fill="none" stroke="#2b5fa8" stroke-width="5"/>'
        f'<g style="mix-blend-mode:screen">{"".join(parts)}</g>'
        '<text x="12" y="296" fill="#4b6a8f" font-size="10" font-family="monospace">'
        'X-RAY  |  주황=유기물  초록=혼합  파랑=금속</text></svg>'
    )


def xray_legend_svg() -> str:
    """판독 가이드용 위험물 견본."""
    kinds = [("pistol", "권총"), ("knife", "칼"), ("ammo", "탄약"), ("drug", "마약 벽돌"), ("bomb", "폭발물"), ("book", "책(무해)")]
    parts = []
    for i, (k, label) in enumerate(kinds):
        x = 60 + i * 100
        parts.append(f'<g transform="translate({x},60) scale(0.8)">{_xray_shape(k)}</g>')
        parts.append(f'<text x="{x}" y="118" fill="#cfd8e3" font-size="12" text-anchor="middle">{label}</text>')
    return ('<svg viewBox="0 0 610 130" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto">'
            f'<rect width="610" height="130" rx="10" fill="#060d18"/>{"".join(parts)}</svg>')


# ---------- 금속탐지기 ----------
ZONE_POS = {
    "머리": (60, 22),
    "몸통": (60, 70),
    "코트 안쪽": (72, 82),
    "허리": (60, 108),
    "손목": (28, 118),
    "주머니": (82, 122),
    "발목": (48, 200),
}


def metal_svg(body: list[Item]) -> str:
    hot = {i.zone for i in body if i.metal}
    marks = "".join(
        f'<circle cx="{ZONE_POS[z][0]}" cy="{ZONE_POS[z][1]}" r="13" fill="#ff3b3b" opacity="0.55">'
        f'<animate attributeName="opacity" values="0.2;0.8;0.2" dur="1s" repeatCount="indefinite"/></circle>'
        for z in hot
    )
    silhouette = (
        '<circle cx="60" cy="22" r="16" fill="#3b4b5f"/>'
        '<path d="M34,42 L86,42 L92,120 L28,120 Z" fill="#3b4b5f"/>'
        '<rect x="18" y="44" width="12" height="76" rx="6" fill="#3b4b5f"/><rect x="90" y="44" width="12" height="76" rx="6" fill="#3b4b5f"/>'
        '<rect x="36" y="118" width="20" height="92" fill="#3b4b5f"/><rect x="64" y="118" width="20" height="92" fill="#3b4b5f"/>'
    )
    status = (
        '<text x="60" y="232" fill="#ff6b6b" font-size="13" text-anchor="middle" font-weight="bold">삐— 금속 반응</text>'
        if hot else '<text x="60" y="232" fill="#5fd38d" font-size="13" text-anchor="middle" font-weight="bold">반응 없음</text>'
    )
    return (
        '<svg viewBox="0 0 120 240" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:200px;height:auto">'
        '<rect width="120" height="240" rx="10" fill="#0d1622"/>'
        f'{silhouette}{marks}{status}</svg>'
    )
