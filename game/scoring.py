ACTION_LABELS = {"APPROVE": "입국 승인", "DENY": "입국 거부", "ARREST": "체포"}
REASON_BONUS = 5
TERRORIST_BONUS = 20

# (정답 조치, 플레이어 조치) → 점수
POINTS = {
    ("APPROVE", "APPROVE"): 10,
    ("APPROVE", "DENY"): -10,
    ("APPROVE", "ARREST"): -20,
    ("DENY", "DENY"): 10,
    ("DENY", "ARREST"): -5,
    ("DENY", "APPROVE"): -15,
    ("ARREST", "ARREST"): 20,
    ("ARREST", "DENY"): 3,
    ("ARREST", "APPROVE"): -30,
}


def score_decision(expected: str, action: str, terrorist: bool, reasons: list[str], violations: list[str]) -> dict:
    points = POINTS[(expected, action)]
    if terrorist and expected == "ARREST":
        if action == "ARREST":
            points += TERRORIST_BONUS
        elif action == "APPROVE":
            points = -60
    reason_ok = action == expected != "APPROVE" and set(reasons) == set(violations)
    if reason_ok:
        points += REASON_BONUS
    # 위험인물 입국 허용 / 무고한 사람 체포 = 치명적 실수 (무한 모드 목숨 차감)
    severe = (expected == "ARREST" and action == "APPROVE") or (expected == "APPROVE" and action == "ARREST")
    return {"points": points, "correct": action == expected, "reason_ok": reason_ok, "severe": severe}


def rank_title(accuracy: float) -> str:
    if accuracy >= 0.9:
        return "국경의 수호자"
    if accuracy >= 0.75:
        return "베테랑 심사관"
    if accuracy >= 0.55:
        return "일반 심사관"
    return "수습 심사관"
