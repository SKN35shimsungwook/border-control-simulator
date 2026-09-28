from dataclasses import dataclass, field
from datetime import date


@dataclass
class Face:
    shape: str = "oval"
    nose: str = "straight"
    lips: str = "medium"
    brows: str = "medium"
    eye_size: str = "normal"
    ears: str = "normal"
    freckles: bool = False
    dimples: bool = False


@dataclass
class Person:
    name: str
    sex: str  # "M" / "F"
    age: int
    nationality: str
    skin: str
    hair_color: str
    hair_style: str
    eye: str
    height: int
    glasses: bool
    beard: bool
    mark: str | None  # 겉으로 보이는 특징
    hidden_mark: str | None  # 옷에 가려진 특징
    top: str
    top_color: str
    bottom: str
    bottom_color: str
    hat: str | None
    luggage_color: str
    nervous: bool = False
    bulge: bool = False
    face: Face = field(default_factory=Face)


@dataclass
class Passport:
    name: str
    sex: str
    dob: date
    nationality: str
    number: str
    expiry: date
    seal: str
    eye: str
    height: int
    mark: str | None
    # 사진 속 모습 (판정 기준 아님)
    hair_color: str
    glasses: bool
    beard: bool


@dataclass
class Visa:
    name: str
    passport_no: str
    purpose: str
    max_days: int
    valid_until: date


@dataclass
class Item:
    name: str
    kind: str  # X-ray 도형 종류 또는 "body"
    danger: str | None = None  # "drug" / "weapon" / "explosive"
    metal: bool = False
    zone: str | None = None  # 몸에 지닌 경우 부위


@dataclass
class WantedEntry:
    name: str
    sex: str
    eye: str
    height: int
    mark: str
    crime: str
    terror: bool


@dataclass
class Traveler:
    id: int
    seed: int
    person: Person
    passport: Passport
    visa: Visa | None
    luggage: list[Item]
    body: list[Item]
    answers: dict
    flaws: list[str] = field(default_factory=list)  # 생성기가 심은 결함 (정답 검증용)
