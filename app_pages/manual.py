import streamlit as st

from game import data as D
from game import ui
from game.scoring import POINTS, REASON_BONUS, TERRORIST_BONUS, ACTION_LABELS

st.title(":material/menu_book: 근무 수칙")
st.caption("아르카디아 공화국 국경 심사관 업무 지침서")

with st.container(border=True):
    st.subheader("판정 규칙")
    ui.rulebook(D.ALL_RULES)

with st.container(border=True):
    st.subheader("스토리 모드 일정")
    for day, rules in D.DAY_NEW_RULES.items():
        st.markdown(f"**Day {day}** · " + ", ".join(ui.rule_name(r) for r in rules))

with st.container(border=True):
    st.subheader("검사 도구")
    st.markdown(
        f"""
- **인터뷰** ({D.TOOL_MINUTES['question']}분/질문): 방문 목적·체류 기간 등을 물어 비자와 대조
- **생체 스캔** ({D.TOOL_MINUTES['scan']}분): 실제 눈동자 색·키·겉으로 보이는 특이사항 측정
- **X-ray** ({D.TOOL_MINUTES['xray']}분): 캐리어 내부 투시. 주황=유기물, 초록=혼합, 파랑=금속
- **금속탐지기** ({D.TOOL_MINUTES['metal']}분): 몸에 지닌 금속의 위치 표시 (벨트·열쇠 같은 무해한 금속도 반응)
- **몸수색** ({D.TOOL_MINUTES['search']}분): 몸에 숨긴 물건과 옷에 가려진 문신까지 확인

스토리 모드는 근무 시간(09:00–11:00)이 정해져 있어서 도구를 쓸수록 처리할 수 있는 인원이 줄어듭니다.
판정마다 기본 {D.BASE_MINUTES}분이 걸립니다.
"""
    )

with st.container(border=True):
    st.subheader("점수표")
    rows = [
        {"정답 조치": ACTION_LABELS[exp], "내 조치": ACTION_LABELS[act], "점수": pts}
        for (exp, act), pts in POINTS.items()
    ]
    st.dataframe(rows, hide_index=True)
    st.markdown(
        f"""
- 거부·체포할 때 위반 사유를 **정확히** 고르면 +{REASON_BONUS}
- 테러 용의자를 체포하면 +{TERRORIST_BONUS}, 입국시키면 -60
- **무한 모드**: {D.ENDLESS_SECONDS // 60}분 제한, 목숨 {D.ENDLESS_LIVES}개. 위험인물 입국 허용이나 무고한 사람 체포 시 목숨 -1
"""
    )
