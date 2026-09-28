import streamlit as st

from game.leaderboard import top_scores

st.title(":material/leaderboard: 리더보드")
st.caption("이 서버에 저장된 기록입니다. Streamlit Cloud에서는 앱이 재시작되면 초기화될 수 있습니다.")

mode = st.segmented_control("모드", ["스토리", "무한"], default="스토리", key="lb_mode")
rows = top_scores("story" if mode == "스토리" else "endless")
if not rows:
    st.info("아직 기록이 없습니다. 첫 기록의 주인공이 되어 보세요!", icon=":material/emoji_events:")
else:
    st.dataframe(
        [
            {
                "순위": i + 1,
                "심사관": r["officer"],
                "점수": r["score"],
                "처리 인원": r["processed"],
                "정확도": r["accuracy"],
                "검거": r["caught"],
                "일시": r["created_at"],
            }
            for i, r in enumerate(rows)
        ],
        hide_index=True,
        column_config={"정확도": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1)},
    )
