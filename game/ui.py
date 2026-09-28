"""Streamlit 렌더링 헬퍼 (서류 카드, 수배자 명단, 수칙)."""

import base64
import html

import streamlit as st

from . import art
from . import data as D
from .models import Passport, Person, Visa, WantedEntry
from .scoring import ACTION_LABELS

SEX_KO = {"M": "남", "F": "여"}


def rule_name(code: str) -> str:
    return D.RULES[code][0]


def _img_tag(img: bytes) -> str:
    return f'<img src="data:image/jpeg;base64,{base64.b64encode(img).decode()}" style="width:100px;border-radius:4px"/>'


def passport_card(pp: Passport, p: Person, photo: bytes | None = None) -> None:
    seal_hex = D.SEAL_HEX[pp.seal]
    photo_html = _img_tag(photo) if photo else art.as_img(art.passport_photo_svg(pp, p), "100px")
    rows = [
        ("성명", pp.name),
        ("성별", SEX_KO[pp.sex]),
        ("생년월일", pp.dob.isoformat()),
        ("국적", pp.nationality),
        ("여권번호", pp.number),
        ("만료일", pp.expiry.isoformat()),
        ("키", f"{pp.height} cm"),
        ("눈동자", pp.eye),
        ("특이사항", pp.mark or "없음"),
    ]
    fields = "".join(
        f'<span style="color:#7a6a45">{k}</span><b style="font-family:monospace;word-break:keep-all">{html.escape(str(v))}</b>'
        for k, v in rows
    )
    st.html(
        f"""
<div style="background:linear-gradient(135deg,#f6efdc,#e9dfc2);border:2px solid #b9a77a;border-radius:12px;
            padding:12px 14px;color:#2a2418;font-size:13px;position:relative;box-shadow:0 4px 14px #0005">
  <div style="font-weight:700;letter-spacing:1px;margin:0 60px 10px 0;color:#5b4a26">
    {html.escape(pp.nationality)} · PASSPORT</div>
  <div style="position:absolute;right:12px;top:8px;width:50px;height:50px;border-radius:50%;
              border:4px double {seal_hex};color:{seal_hex};display:flex;align-items:center;justify-content:center;
              font-weight:800;font-size:9px;transform:rotate(-14deg);opacity:.9">OFFICIAL</div>
  <div style="display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap">
    <div style="border:1px solid #b9a77a;padding:2px;background:#fff;width:100px;flex:none">{photo_html}</div>
    <div style="display:grid;grid-template-columns:auto 1fr;column-gap:10px;row-gap:3px;flex:1;min-width:170px">{fields}</div>
  </div>
</div>"""
    )


def visa_card(v: Visa) -> None:
    rows = [
        ("성명", v.name),
        ("여권번호", v.passport_no),
        ("방문 목적", v.purpose),
        ("최대 체류", f"{v.max_days}일"),
        ("유효기간", f"~ {v.valid_until.isoformat()}"),
    ]
    fields = "".join(
        f'<span style="color:#3d5a73">{k}</span><b style="font-family:monospace">{html.escape(str(val))}</b>'
        for k, val in rows
    )
    st.html(
        f"""
<div style="background:linear-gradient(135deg,#dcecf6,#c3dbe9);border:2px solid #7ea6c2;border-radius:12px;
            padding:12px 14px;color:#14283a;font-size:14px;box-shadow:0 4px 14px #0005">
  <div style="font-weight:700;letter-spacing:1px;margin-bottom:6px;color:#23486a">{D.HOME} 입국 비자 · VISA</div>
  <div style="display:grid;grid-template-columns:auto 1fr;column-gap:10px;row-gap:3px">{fields}</div>
</div>"""
    )


def wanted_cards(wanted: list[WantedEntry]) -> None:
    if not wanted:
        st.caption("오늘은 수배자 명단이 없습니다.")
        return
    for w in wanted:
        with st.container(border=True):
            badge = ":red-badge[:material/warning: 테러]" if w.terror else ":orange-badge[범죄]"
            st.markdown(f"**{w.name}** {badge}  \n죄목: {w.crime}")
            st.caption(f"{SEX_KO[w.sex]} · 눈동자 {w.eye} · 약 {w.height}cm · 특징: **{w.mark}**")


def rulebook(rules: list[str], new_rules: list[str] | None = None) -> None:
    new_rules = new_rules or []
    for code in rules:
        name, action, desc = D.RULES[code]
        new = " :blue-badge[NEW]" if code in new_rules else ""
        act = ":red[체포]" if action == "ARREST" else ":orange[거부]"
        st.markdown(f"**{name}** → {act}{new}  \n{desc}")
    if {"SEAL", "PASSPORT_NO", "VISA"} & set(rules):
        st.markdown("**국가별 정보**")
        rows = []
        for name, c in D.COUNTRIES.items():
            color = D.SEAL_HEX[c["seal"]]
            rows.append(
                f'<tr><td>{name}</td><td style="font-family:monospace">{c["code"]}-0000000</td>'
                f'<td><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{color};'
                f'vertical-align:middle"></span> {c["seal"]}</td><td>{"필요" if c["visa"] and "VISA" in rules else "-"}</td></tr>'
            )
        st.html(
            '<table style="width:100%;font-size:13px;border-collapse:collapse">'
            "<tr style='text-align:left;opacity:.7'><th>국가</th><th>여권번호 형식</th><th>도장 색</th><th>비자</th></tr>"
            f'{"".join(rows)}</table>'
        )
    if {"CONTRABAND", "WEAPON"} & set(rules):
        st.markdown("**X-ray 판독 가이드**")
        st.html(art.as_img(art.xray_legend_svg()))


def log_rows(entries: list[dict]) -> list[dict]:
    return [
        {
            "결과": "✅" if e["correct"] else "❌",
            "이름": e["name"],
            "국적": e["nationality"],
            "내 판정": ACTION_LABELS[e["action"]],
            "정답": ACTION_LABELS[e["expected"]],
            "위반 사항": ", ".join(rule_name(v) for v in e["violations"]) or "-",
            "테러": "⚠️" if e["terrorist"] else "",
            "점수": e["points"],
        }
        for e in entries
    ]
