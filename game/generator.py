"""여행자·수배자 무작위 생성. 결함(위반)을 일부러 심고, 그 목록을 Traveler.flaws에 기록한다."""

import random
from datetime import date, timedelta

from . import data as D
from .models import Face, Item, Passport, Person, Traveler, Visa, WantedEntry

FLAW_WEIGHTS = {
    "EXPIRED": 2,
    "SEAL": 2,
    "PHOTO": 2,
    "WANTED": 3,
    "VISA": 2,
    "INTERVIEW": 2,
    "CONTRABAND": 2,
    "WEAPON": 2,
    "PASSPORT_NO": 2,
}


def _name(rng: random.Random, sex: str, taken: set[str]) -> str:
    firsts = D.MALE_NAMES if sex == "M" else D.FEMALE_NAMES
    while True:
        n = f"{rng.choice(firsts)} {rng.choice(D.SURNAMES)}"
        if n not in taken:
            return n


def _height(rng: random.Random, sex: str) -> int:
    return rng.randint(165, 192) if sex == "M" else rng.randint(152, 180)


def _mix(a: str, b: str, t: float) -> str:
    ca = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def random_skin(rng: random.Random) -> str:
    """연속 피부톤: 기준색 사이를 보간하고 따뜻함/차가움을 살짝 흔든다."""
    stops = D.SKIN_STOPS
    pos = rng.random() * (len(stops) - 1)
    i = min(int(pos), len(stops) - 2)
    base = _mix(stops[i], stops[i + 1], pos - i)
    tint = "#e0a080" if rng.random() < 0.5 else "#c8a898"
    return _mix(base, tint, rng.uniform(0, 0.12))


def random_face(rng: random.Random) -> Face:
    return Face(
        shape=rng.choice(list(D.FACE_SHAPES)),
        nose=rng.choice(list(D.NOSES)),
        lips=rng.choice(list(D.LIPS)),
        brows=rng.choice(list(D.BROWS)),
        eye_size=rng.choices(list(D.EYE_SIZES), weights=[1, 3, 1])[0],
        ears=rng.choices(list(D.EARS), weights=[1, 3, 1])[0],
        freckles=rng.random() < 0.15,
        dimples=rng.random() < 0.15,
    )


def random_hair_style(rng: random.Random, sex: str, age: int) -> str:
    weights = dict(D.HAIR_WEIGHTS[sex])
    if sex == "M" and age < 40:
        weights.pop("대머리", None)
    return rng.choices(list(weights), weights=list(weights.values()))[0]


def make_wanted_list(rng: random.Random, n: int) -> list[WantedEntry]:
    marks = list(D.VISIBLE_MARKS) + list(D.HIDDEN_MARKS)
    rng.shuffle(marks)
    crimes = D.CRIMES[:]
    rng.shuffle(crimes)
    wanted, names = [], set()
    for i in range(n):
        sex = rng.choice("MF")
        name = _name(rng, sex, names)
        names.add(name)
        crime, terror = crimes[i % len(crimes)]
        wanted.append(
            WantedEntry(
                name=name,
                sex=sex,
                eye=rng.choice(list(D.EYE_COLORS)),
                height=_height(rng, sex),
                mark=marks[i],
                crime=crime,
                terror=terror,
            )
        )
    # 최소 한 명은 테러 관련 수배자로
    if not any(w.terror for w in wanted):
        wanted[0].crime, wanted[0].terror = "테러 모의", True
    return wanted


def _applicable_flaws(rules: list[str], nationality: str, wanted: list[WantedEntry]) -> list[str]:
    out = []
    for r in rules:
        if r == "WANTED" and not wanted:
            continue
        if r == "VISA" and not D.COUNTRIES[nationality]["visa"]:
            continue
        if r == "INTERVIEW" and nationality == D.HOME:
            continue
        out.append(r)
    return out


def _pick_flaws(rng: random.Random, candidates: list[str], p_bad: float) -> list[str]:
    if not candidates or rng.random() >= p_bad:
        return []
    count = 2 if (len(candidates) > 1 and rng.random() < 0.15) else 1
    flaws = []
    pool = candidates[:]
    for _ in range(count):
        f = rng.choices(pool, weights=[FLAW_WEIGHTS[c] for c in pool])[0]
        flaws.append(f)
        pool.remove(f)
    return flaws


def _passport_number(rng: random.Random, code: str) -> str:
    return f"{code}-{rng.randint(0, 9_999_999):07d}"


def make_traveler(
    rng: random.Random,
    tid: int,
    today: date,
    rules: list[str],
    wanted: list[WantedEntry],
    p_bad: float,
) -> Traveler:
    seed = rng.randint(1, 2**31 - 1)
    wanted_marks = {w.mark for w in wanted}
    wanted_names = {w.name for w in wanted}
    free_visible = [m for m in D.VISIBLE_MARKS if m not in wanted_marks]
    free_hidden = [m for m in D.HIDDEN_MARKS if m not in wanted_marks]

    countries = list(D.COUNTRIES)
    nationality = rng.choices(countries, weights=[4 if c == D.HOME else 2 for c in countries])[0]
    needs_visa = D.COUNTRIES[nationality]["visa"]
    foreign = nationality != D.HOME
    flaws = _pick_flaws(rng, _applicable_flaws(rules, nationality, wanted), p_bad)

    # ---- 인물 ----
    sex = rng.choice("MF")
    age = rng.randint(19, 72)
    person = Person(
        name="",
        sex=sex,
        age=age,
        nationality=nationality,
        skin=random_skin(rng),
        hair_color=rng.choice(list(D.HAIR_COLORS)),
        hair_style=random_hair_style(rng, sex, age),
        eye=rng.choice(list(D.EYE_COLORS)),
        height=_height(rng, sex),
        glasses=rng.random() < 0.25,
        beard=sex == "M" and rng.random() < 0.3,
        mark=rng.choice(free_visible) if (free_visible and rng.random() < 0.35) else None,
        hidden_mark=rng.choice(free_hidden) if (free_hidden and rng.random() < 0.2) else None,
        top=rng.choice(list(D.TOPS)),
        top_color=rng.choice(list(D.CLOTH_COLORS)),
        bottom=rng.choice(list(D.BOTTOMS)),
        bottom_color=rng.choice(list(D.CLOTH_COLORS)),
        hat=rng.choice(list(D.HATS)),
        luggage_color=rng.choice(list(D.LUGGAGE_COLORS)),
        face=random_face(rng),
    )
    if person.age > 55 and rng.random() < 0.5:
        person.hair_color = "회색"
    passport_name = None

    if "WANTED" in flaws:
        w = rng.choice(wanted)
        if person.sex != w.sex:
            person.sex = w.sex
            person.hair_style = random_hair_style(rng, w.sex, person.age)
        person.beard = person.beard and w.sex == "M"
        person.eye = w.eye
        person.height = w.height + rng.randint(-2, 2)
        if w.mark in D.VISIBLE_MARKS:
            person.mark = w.mark
        else:
            person.hidden_mark = w.mark
        # 절반은 본명, 절반은 가명 여권 (가명이면 특징으로 찾아야 함)
        passport_name = w.name if rng.random() < 0.5 else _name(rng, w.sex, wanted_names)
    person.name = passport_name or _name(rng, person.sex, wanted_names)

    # ---- 여권 ----
    code = D.COUNTRIES[nationality]["code"]
    passport = Passport(
        name=person.name,
        sex=person.sex,
        dob=today - timedelta(days=person.age * 365 + rng.randint(0, 364)),
        nationality=nationality,
        number=_passport_number(rng, code),
        expiry=today + timedelta(days=rng.randint(20, 3000)),
        seal=D.COUNTRIES[nationality]["seal"],
        eye=person.eye,
        height=person.height + rng.randint(-3, 3),
        mark=person.mark,
        hair_color=person.hair_color if rng.random() < 0.85 else rng.choice(list(D.HAIR_COLORS)),
        glasses=person.glasses if rng.random() < 0.8 else not person.glasses,
        beard=person.beard if rng.random() < 0.85 else (person.sex == "M" and not person.beard),
    )
    if "EXPIRED" in flaws:
        passport.expiry = today - timedelta(days=rng.randint(1, 500))
    if "SEAL" in flaws:
        passport.seal = rng.choice([s for s in D.SEAL_HEX if s != passport.seal])
    if "PASSPORT_NO" in flaws:
        kind = rng.randrange(3)
        if kind == 0:
            other = rng.choice([c["code"] for c in D.COUNTRIES.values() if c["code"] != code])
            passport.number = _passport_number(rng, other)
        elif kind == 1:
            passport.number = f"{code}-{rng.randint(0, 999_999):06d}"
        else:
            digits = list(f"{rng.randint(0, 9_999_999):07d}")
            digits[rng.randrange(7)] = rng.choice("ABXZ")
            passport.number = f"{code}-{''.join(digits)}"
    if "PHOTO" in flaws:
        kind = rng.choice(["eye", "mark", "height", "height", "sex"])
        if kind == "eye":
            passport.eye = rng.choice([e for e in D.EYE_COLORS if e != person.eye])
        elif kind == "mark":
            options = [None] + [m for m in free_visible if m != person.mark]
            passport.mark = rng.choice([m for m in options if m != person.mark])
        elif kind == "height":
            passport.height = person.height + rng.choice([-1, 1]) * rng.randint(12, 20)
        else:
            passport.sex = "F" if person.sex == "M" else "M"

    # ---- 비자 ----
    visa = None
    if "VISA" in rules and needs_visa:
        visa = Visa(
            name=passport.name,
            passport_no=passport.number,
            purpose=rng.choice(D.PURPOSES),
            max_days=rng.choice([14, 30, 60, 90]),
            valid_until=today + timedelta(days=rng.randint(10, 300)),
        )
        if "VISA" in flaws:
            kind = rng.choice(["missing", "missing", "name", "number", "expired"])
            if kind == "missing":
                visa = None
            elif kind == "name":
                visa.name = _name(rng, person.sex, wanted_names | {passport.name})
            elif kind == "number":
                digits = list(passport.number[-7:])
                i = rng.randrange(len(digits))
                digits[i] = str((int(digits[i]) + rng.randint(1, 9)) % 10) if digits[i].isdigit() else "7"
                visa.passport_no = passport.number[:-7] + "".join(digits)
            else:
                visa.valid_until = today - timedelta(days=rng.randint(1, 200))

    # ---- 인터뷰 답변 ----
    if not foreign:
        answers = {"purpose": "귀국", "days": 0}
    elif visa is not None:
        answers = {"purpose": visa.purpose, "days": rng.randint(3, visa.max_days)}
    else:
        answers = {"purpose": rng.choice(D.PURPOSES[:3]), "days": rng.randint(2, D.NO_VISA_MAX_DAYS)}
    if "INTERVIEW" in flaws:
        if visa is not None and rng.random() < 0.5:
            answers["purpose"] = rng.choice([p for p in D.PURPOSES if p != visa.purpose])
        else:
            limit = visa.max_days if visa is not None else D.NO_VISA_MAX_DAYS
            answers["days"] = limit + rng.randint(10, 120)
    answers["origin"] = nationality if rng.random() < 0.8 else rng.choice(countries)
    answers["lodging"] = "자택" if not foreign else rng.choice(D.LODGINGS)
    answers["job"] = rng.choice(D.JOBS)

    # ---- 소지품 ----
    luggage = [Item(n, k) for n, k in rng.sample(D.LUGGAGE_SAFE, rng.randint(4, 6))]
    body = [Item(n, "body", metal=m, zone=z) for n, m, z in rng.sample(D.BODY_SAFE, rng.randint(1, 3))]
    if person.top in D.BULKY_TOPS and rng.random() < 0.15:
        n, m, z = D.BODY_BULGE_SAFE
        body.append(Item(n, "body", metal=m, zone=z))
        person.bulge = True

    def hide_on_body(danger: str):
        n, m, z = rng.choice(D.BODY_DANGER[danger])
        body.append(Item(n, "body", danger=danger, metal=m, zone=z))
        if z in ("코트 안쪽", "몸통"):
            person.bulge = True
            if person.top not in D.BULKY_TOPS:
                person.top = rng.choice(D.BULKY_TOPS)

    def pack(danger: str):
        n, k = rng.choice(D.LUGGAGE_DANGER[danger])
        luggage.insert(rng.randint(0, len(luggage)), Item(n, k, danger=danger, metal=k != "drug"))

    if "CONTRABAND" in flaws:
        pack("drug") if rng.random() < 0.6 else hide_on_body("drug")
    if "WEAPON" in flaws:
        danger = "explosive" if rng.random() < 0.3 else "weapon"
        pack(danger) if rng.random() < 0.55 else hide_on_body(danger)

    person.nervous = rng.random() < (0.45 if flaws else 0.12)
    return Traveler(
        id=tid,
        seed=seed,
        person=person,
        passport=passport,
        visa=visa,
        luggage=luggage,
        body=body,
        answers=answers,
        flaws=flaws,
    )
