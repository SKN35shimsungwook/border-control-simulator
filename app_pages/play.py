import streamlit as st

from game import ai_images, art, ui
from game import data as D
from game.engine import Game
from game.leaderboard import add_score
from game.scoring import ACTION_LABELS, rank_title

g: Game | None = st.session_state.game
ai_provider = ai_images.provider()

QUESTIONS = {
    "purpose": "방문 목적이 무엇입니까?",
    "days": "얼마나 머무를 예정입니까?",
    "origin": "어디에서 오셨습니까?",
    "lodging": "어디서 지내실 겁니까?",
    "job": "직업이 무엇입니까?",
}


def answer_text(t, key: str) -> str:
    a = t.answers
    home = t.person.nationality == D.HOME
    text = {
        "purpose": "집에 돌아오는 길입니다." if home else f"{a['purpose']} 목적입니다.",
        "days": "여기 사는 사람이에요." if home else f"{a['days']}일 정도 있을 거예요.",
        "origin": f"{a['origin']}에서 왔습니다.",
        "lodging": f"{a['lodging']}에서 지낼 겁니다.",
        "job": f"{a['job']}입니다.",
    }[key]
    return ("어… 그러니까… " + text) if t.person.nervous else text


def caught_count(game: Game) -> int:
    return sum(1 for e in game.log if e["expected"] == "ARREST" and e["action"] == "ARREST")


def save_score(game: Game):
    if not game.saved and game.log and st.session_state.officer.strip():
        add_score(st.session_state.officer.strip(), game.mode, game.score, len(game.log), game.accuracy, caught_count(game))
        game.saved = True


# ===================== 사이드바 =====================
with st.sidebar:
    st.header(":material/badge: 국경 심사관")
    if g is not None:
        st.caption(f"심사관 **{st.session_state.officer or '익명'}** · {'스토리' if g.mode == 'story' else '무한'} 모드")
        c1, c2 = st.columns(2)
        c1.metric("점수", g.score)
        c2.metric("정확도", f"{g.accuracy:.0%}" if g.log else "-")
        if g.mode == "story":
            c1.metric("근무일", f"Day {g.day}")
            c2.metric("시각", g.clock_text(), help=f"근무 종료 {D.SHIFT_END // 60:02d}:00")
        else:
            c1.metric("목숨", f"{g.lives} / {D.ENDLESS_LIVES}")
            c2.metric("처리", f"{len(g.log)}명")
        if st.button("근무 포기", icon=":material/logout:", width="stretch"):
            g.phase = "over"
            st.rerun()
    if ai_provider:
        st.toggle(f"AI 이미지 ({ai_provider})", key="use_ai")
    else:
        st.caption(":material/image: SVG 일러스트 사용 중. secrets에 `POLLINATIONS_API_KEY` 또는 `OPENAI_API_KEY`를 넣으면 AI 이미지로 바뀝니다.")

use_ai = bool(ai_provider and st.session_state.use_ai)

# 무한 모드 타이머
if g is not None and g.mode == "endless" and g.phase == "inspect":

    @st.fragment(run_every=1)
    def timer():
        if g.check_timeout():
            st.rerun()
        left = max(0, int(g.time_left()))
        st.progress(left / D.ENDLESS_SECONDS, text=f"남은 시간 {left // 60}:{left % 60:02d}")

    with st.sidebar:
        timer()

# ===================== 메뉴 =====================
if g is None:
    st.title("국경 심사관")
    st.markdown(
        f"당신은 **{D.HOME} 공화국** 국경 검문소의 심사관입니다. 여권·비자·인상착의·소지품을 확인해 "
        "**입국 승인 / 입국 거부 / 체포** 중 하나를 결정하세요. 테러리스트와 수배자를 놓치면 큰일 납니다."
    )
    with st.container(border=True):
        # 위젯 키는 위젯이 사라지면 지워지므로 별도 키에 보관
        st.session_state.officer = st.text_input(
            "심사관 이름 (리더보드 기록용)", value=st.session_state.officer, max_chars=20, placeholder="예: 김심사"
        )
        mode = st.segmented_control(
            "모드",
            ["스토리", "무한"],
            default="스토리",
            key="mode_pick",
            help="스토리: Day 1–5 동안 날마다 규칙이 늘어남 / 무한: 모든 규칙, 5분 제한, 목숨 3개",
        )
        if mode == "스토리":
            st.caption(f"Day 1–{D.STORY_DAYS} · 근무 시간 09:00–11:00 · 도구 사용 시 시간 소모")
        else:
            st.caption(f"모든 규칙 적용 · 실제 시간 {D.ENDLESS_SECONDS // 60}분 · 치명적 실수 {D.ENDLESS_LIVES}번이면 해고")
        if st.button("근무 시작", type="primary", icon=":material/play_arrow:", disabled=mode is None):
            st.session_state.game = Game.new("story" if mode == "스토리" else "endless")
            st.rerun()
    st.stop()

# ===================== 브리핑 =====================
if g.phase == "briefing":
    if g.mode == "story":
        st.title(f"Day {g.day} · {g.today.isoformat()}")
        st.markdown("오늘 새로 적용되는 규칙:")
    else:
        st.title("무한 모드 브리핑")
        st.markdown("모든 규칙이 적용됩니다.")
    left, right = st.columns([3, 2])
    with left, st.container(border=True):
        ui.rulebook(g.new_rules, g.new_rules if g.mode == "story" and g.day > 1 else [])
        if g.mode == "story" and g.day > 1:
            prev = [r for r in g.rules if r not in g.new_rules]
            st.caption("기존 규칙도 계속 적용: " + ", ".join(ui.rule_name(r) for r in prev))
    with right, st.container(border=True):
        st.subheader(":material/person_search: 오늘의 수배자")
        ui.wanted_cards(g.wanted)
    if st.button("근무 시작", type="primary", icon=":material/play_arrow:"):
        g.start_shift()
        st.rerun()
    st.stop()

# ===================== 하루 종료 =====================
if g.phase == "day_end":
    entries = g.day_entries()
    st.title(f"Day {g.day} 근무 종료")
    c1, c2, c3 = st.columns(3)
    c1.metric("처리 인원", f"{len(entries)}명")
    c2.metric("정답", f"{sum(e['correct'] for e in entries)}명")
    c3.metric("오늘 점수", sum(e["points"] for e in entries))
    st.dataframe(ui.log_rows(entries), hide_index=True)
    last = g.day >= D.STORY_DAYS
    if st.button("최종 평가 보기" if last else f"Day {g.day + 1}로", type="primary", icon=":material/arrow_forward:"):
        g.next_day()
        st.rerun()
    st.stop()

# ===================== 게임 종료 =====================
if g.phase == "over":
    save_score(g)
    st.title("근무 평가")
    st.subheader(f":material/workspace_premium: {rank_title(g.accuracy)}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("최종 점수", g.score)
    c2.metric("처리 인원", f"{len(g.log)}명")
    c3.metric("정확도", f"{g.accuracy:.0%}" if g.log else "-")
    c4.metric("검거", f"{caught_count(g)}명")
    missed = [e for e in g.log if e["expected"] == "ARREST" and e["action"] == "APPROVE"]
    if missed:
        st.error(f"위험인물 {len(missed)}명이 입국했습니다: " + ", ".join(e["name"] for e in missed), icon=":material/dangerous:")
    if g.saved:
        st.success("리더보드에 기록했습니다.", icon=":material/leaderboard:")
    elif not st.session_state.officer.strip():
        st.caption("심사관 이름이 없어 리더보드에 기록하지 않았습니다.")
    if g.log:
        st.dataframe(ui.log_rows(g.log), hide_index=True)
    with st.container(horizontal=True):
        if st.button("같은 모드로 다시", type="primary", icon=":material/replay:"):
            st.session_state.game = Game.new(g.mode)
            st.rerun()
        if st.button("메뉴로", icon=":material/home:"):
            st.session_state.game = None
            st.rerun()
    st.stop()

# ===================== 심사 =====================
t = g.current
p, pp = t.person, t.passport

fb = g.last_feedback
if fb:
    label = f"직전: **{fb['name']}** → {ACTION_LABELS[fb['action']]} ({fb['points']:+d}점)"
    why = ", ".join(ui.rule_name(v) for v in fb["violations"]) or "위반 없음"
    if fb["correct"]:
        extra = " · 사유 정확 보너스" if fb["reason_ok"] else ""
        st.success(f"{label} — 정답! ({why}{extra})", icon=":material/check_circle:")
    else:
        st.error(f"{label} — 정답은 {ACTION_LABELS[fb['expected']]} ({why})", icon=":material/cancel:")

body_job = portrait_job = None
if use_ai:
    body_job = ai_images.request(f"b{g.seed}-{t.id}", ai_images.body_prompt(p), t.seed, 512, 768)
    portrait_job = ai_images.request(f"p{g.seed}-{t.id}", ai_images.portrait_prompt(pp, p), t.seed + 1, 384, 480)
body_img = ai_images.result(body_job)
portrait_img = ai_images.result(portrait_job)

col_booth, col_docs, col_tools = st.columns([1, 1.35, 1.65], gap="medium")

with col_booth, st.container(border=True):
    st.markdown(f"**:material/person: {len(g.log) + 1}번째 입국자**")
    if isinstance(body_img, bytes):
        st.image(body_img)
    else:
        st.html(art.as_img(art.person_svg(p)))
        if use_ai and body_img is None:

            @st.fragment(run_every=3)
            def wait_for_ai():
                if ai_images.result(body_job) is not None and ai_images.result(portrait_job) is not None:
                    st.rerun()
                st.caption(":material/hourglass_top: AI 이미지 생성 중… 준비되면 바뀝니다.")

            wait_for_ai()
        elif use_ai:
            st.caption("AI 이미지를 불러오지 못해 일러스트로 표시합니다.")
    hat = f", {p.hat}" if p.hat else ""
    st.caption(
        f"복장: {p.top_color} {p.top}, {p.bottom_color} {p.bottom}{hat}  \n"
        f"캐리어: {p.luggage_color}"
    )
    notes = []
    if p.bulge:
        notes.append("상의 안쪽이 불룩하다")
    if p.nervous:
        notes.append("땀을 흘리며 초조해 보인다")
    if notes:
        st.warning(" · ".join(notes), icon=":material/visibility:")

with col_docs:
    st.markdown(f"**:material/description: 제출 서류** · 오늘 {g.today.isoformat()}")
    ui.passport_card(pp, p, portrait_img if isinstance(portrait_img, bytes) else None)
    if t.visa:
        ui.visa_card(t.visa)
    elif "VISA" in g.rules and p.nationality != D.HOME:
        st.caption("비자 서류 없음")

with col_tools:
    tabs = st.tabs(
        [
            ":material/forum: 인터뷰",
            ":material/fingerprint: 생체 스캔",
            ":material/luggage: X-ray",
            ":material/sensors: 금속탐지",
            ":material/back_hand: 몸수색",
            ":material/person_search: 수배자",
            ":material/rule: 수칙",
        ]
    )
    cost = (lambda k: f" ({D.TOOL_MINUTES[k]}분)") if g.mode == "story" else (lambda k: "")

    with tabs[0]:
        with st.container(horizontal=True):
            for key, q in QUESTIONS.items():
                if st.button(q, key=f"q_{t.id}_{key}", disabled=key in g.asked):
                    g.ask(key)
                    st.rerun()
        if not g.asked:
            st.caption(f"질문을 눌러 인터뷰하세요.{cost('question')}")
        for key in g.asked:
            with st.chat_message("user", avatar=":material/badge:"):
                st.write(QUESTIONS[key])
            with st.chat_message("assistant", avatar=":material/person:"):
                st.write(answer_text(t, key))

    with tabs[1]:
        if "scan" in g.revealed:
            c1, c2 = st.columns(2)
            c1.metric("측정 키", f"{p.height} cm")
            c2.metric("눈동자 색", p.eye)
            st.markdown(f"보이는 특이사항: **{p.mark or '없음'}**")
            st.caption("성별: " + ui.SEX_KO[p.sex] + " · 옷에 가려진 부분은 몸수색으로 확인하세요.")
        elif st.button(f"생체 스캔 실행{cost('scan')}", icon=":material/fingerprint:", key=f"scan_{t.id}"):
            g.use_tool("scan")
            st.rerun()

    with tabs[2]:
        if "xray" in g.revealed:
            st.html(art.as_img(art.xray_svg(t.luggage, t.seed)))
            st.caption("수칙 탭에 X-ray 판독 가이드가 있습니다.")
        elif st.button(f"캐리어 X-ray 투시{cost('xray')}", icon=":material/luggage:", key=f"xray_{t.id}"):
            g.use_tool("xray")
            st.rerun()

    with tabs[3]:
        if "metal" in g.revealed:
            c1, c2 = st.columns([1, 1.4])
            with c1:
                st.html(art.as_img(art.metal_svg(t.body), "200px"))
            with c2:
                zones = sorted({i.zone for i in t.body if i.metal}, key=D.BODY_ZONES.index)
                if zones:
                    st.markdown("반응 부위: " + ", ".join(f"**{z}**" for z in zones))
                    st.caption("벨트·열쇠·동전 같은 무해한 금속도 반응합니다. 확실히 하려면 몸수색하세요.")
                else:
                    st.markdown("금속 반응 없음")
                    st.caption("금속이 아닌 물건(마약 등)은 탐지되지 않습니다.")
        elif st.button(f"금속탐지기 통과{cost('metal')}", icon=":material/sensors:", key=f"metal_{t.id}"):
            g.use_tool("metal")
            st.rerun()

    with tabs[4]:
        if "search" in g.revealed:
            for item in t.body:
                icon = ":material/dangerous:" if item.danger else ":material/check:"
                color = "red" if item.danger else "gray"
                st.markdown(f"{icon} :{color}[**{item.name}**] — {item.zone}")
            st.markdown(f"옷 속 신체 특징: **{p.hidden_mark or '없음'}**")
        elif st.button(f"몸수색 실시{cost('search')}", icon=":material/back_hand:", key=f"search_{t.id}"):
            g.use_tool("search")
            st.rerun()

    with tabs[5]:
        ui.wanted_cards(g.wanted)

    with tabs[6]:
        ui.rulebook(g.rules)

with st.container(border=True):
    reasons = st.pills(
        "거부·체포 사유 (정확히 고르면 보너스 +5)",
        g.rules,
        selection_mode="multi",
        format_func=ui.rule_name,
        key=f"reasons_{t.id}",
    )
    with st.container(horizontal=True):
        if st.button("입국 승인", type="primary", icon=":material/check_circle:", key=f"ok_{t.id}"):
            g.decide("APPROVE", [])
            st.rerun()
        if st.button("입국 거부", icon=":material/block:", key=f"deny_{t.id}"):
            g.decide("DENY", reasons or [])
            st.rerun()
        if st.button("체포", icon=":material/local_police:", key=f"arrest_{t.id}"):
            g.decide("ARREST", reasons or [])
            st.rerun()
