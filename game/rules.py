"""판정 기준. 생성기와 독립적으로 여행자의 실제 데이터만 보고 위반 사항을 계산한다."""

import re
from datetime import date

from .data import COUNTRIES, HOME, NO_VISA_MAX_DAYS, RULES
from .models import Traveler, WantedEntry

PHOTO_HEIGHT_TOLERANCE = 7


def matches_wanted(t: Traveler, w: WantedEntry) -> bool:
    p = t.person
    if t.passport.name == w.name:
        return True
    marks = {p.mark, p.hidden_mark}
    return p.sex == w.sex and p.eye == w.eye and w.mark in marks


def find_violations(t: Traveler, rules: list[str], today: date, wanted: list[WantedEntry]) -> list[str]:
    p, pp, v = t.person, t.passport, t.visa
    foreign = p.nationality != HOME
    needs_visa = COUNTRIES[p.nationality]["visa"]
    found = []

    if "EXPIRED" in rules and pp.expiry < today:
        found.append("EXPIRED")
    if "SEAL" in rules and pp.seal != COUNTRIES[pp.nationality]["seal"]:
        found.append("SEAL")
    if "PHOTO" in rules and (
        pp.sex != p.sex
        or pp.eye != p.eye
        or pp.mark != p.mark
        or abs(pp.height - p.height) > PHOTO_HEIGHT_TOLERANCE
    ):
        found.append("PHOTO")
    if "WANTED" in rules and any(matches_wanted(t, w) for w in wanted):
        found.append("WANTED")
    if "VISA" in rules and needs_visa:
        if v is None or v.name != pp.name or v.passport_no != pp.number or v.valid_until < today:
            found.append("VISA")
    if "INTERVIEW" in rules and foreign:
        a = t.answers
        limit = v.max_days if (needs_visa and v is not None) else NO_VISA_MAX_DAYS
        if (needs_visa and v is not None and a["purpose"] != v.purpose) or a["days"] > limit:
            found.append("INTERVIEW")
    carried = t.luggage + t.body
    if "CONTRABAND" in rules and any(i.danger == "drug" for i in carried):
        found.append("CONTRABAND")
    if "WEAPON" in rules and any(i.danger in ("weapon", "explosive") for i in carried):
        found.append("WEAPON")
    if "PASSPORT_NO" in rules:
        code = COUNTRIES[pp.nationality]["code"]
        if not re.fullmatch(rf"{code}-\d{{7}}", pp.number):
            found.append("PASSPORT_NO")
    return found


def expected_action(violations: list[str]) -> str:
    if any(RULES[v][1] == "ARREST" for v in violations):
        return "ARREST"
    if violations:
        return "DENY"
    return "APPROVE"


def is_terrorist(t: Traveler, violations: list[str], wanted: list[WantedEntry]) -> bool:
    if "WEAPON" in violations and any(i.danger == "explosive" for i in t.luggage + t.body):
        return True
    if "WANTED" in violations:
        return any(w.terror and matches_wanted(t, w) for w in wanted)
    return False
