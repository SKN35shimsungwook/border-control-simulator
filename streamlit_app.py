import streamlit as st

st.set_page_config(page_title="국경 심사관", page_icon=":material/badge:", layout="wide")

st.session_state.setdefault("game", None)
st.session_state.setdefault("officer", "")
st.session_state.setdefault("use_ai", True)

page = st.navigation(
    [
        st.Page("app_pages/play.py", title="심사 근무", icon=":material/badge:", default=True),
        st.Page("app_pages/manual.py", title="근무 수칙", icon=":material/menu_book:"),
        st.Page("app_pages/gallery.py", title="입국자 갤러리", icon=":material/groups:"),
        st.Page("app_pages/leaderboard.py", title="리더보드", icon=":material/leaderboard:"),
    ]
)
page.run()
