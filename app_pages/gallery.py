import random

import streamlit as st

from game import art
from game import data as D
from game.generator import make_traveler

st.title(":material/groups: 입국자 갤러리")
st.caption("얼굴형·코·입술·눈썹·헤어·피부톤을 조합해 매번 새로 만드는 가상 인물입니다. 실존 인물을 재현하지 않습니다.")

with st.container(horizontal=True, vertical_alignment="bottom"):
    if st.button("새로 뽑기", icon=":material/casino:"):
        st.session_state.gallery_seed = random.randrange(1, 10**9)
    view = st.segmented_control("보기", ["전신", "여권 사진"], default="전신", key="gallery_view")

rng = random.Random(st.session_state.setdefault("gallery_seed", 1))
people = [make_traveler(rng, i, D.START_DATE, [], [], 0.0) for i in range(12)]

cols = st.columns(6)
for i, t in enumerate(people):
    p = t.person
    with cols[i % 6], st.container(border=True):
        svg = art.passport_photo_svg(t.passport, p) if view == "여권 사진" else art.person_svg(p)
        st.html(art.as_img(svg))
        st.caption(f"{p.age}세 · {p.nationality}  \n{p.hair_color} {p.hair_style} · 눈 {p.eye}")
