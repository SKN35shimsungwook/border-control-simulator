"""게임에 쓰이는 고정 데이터: 가상 국가, 외모 특징, 복장, 소지품, 규칙."""

from datetime import date

HOME = "아르카디아"
START_DATE = date(2026, 10, 1)

# 모든 국가는 가상 국가입니다. 범죄자·테러리스트 배정은 국적과 무관하게 무작위입니다.
COUNTRIES = {
    "아르카디아": {"code": "ARC", "seal": "파랑", "visa": False},
    "노르데니아": {"code": "NRD", "seal": "초록", "visa": False},
    "카스토리아": {"code": "KST", "seal": "빨강", "visa": False},
    "솔라리스": {"code": "SOL", "seal": "주황", "visa": True},
    "베리디아": {"code": "VRD", "seal": "보라", "visa": True},
    "멜로린": {"code": "MLR", "seal": "청록", "visa": True},
}

SEAL_HEX = {
    "파랑": "#2b6cb0",
    "초록": "#2f855a",
    "빨강": "#c53030",
    "주황": "#dd6b20",
    "보라": "#6b46c1",
    "청록": "#0f8f8f",
    "노랑": "#c9a100",
}

MALE_NAMES = ["알렉스", "이반", "레오", "다니엘", "오스카", "루카스", "테오", "마르코", "사무엘", "빅토르", "준", "파블로", "토마스", "하킴", "니코"]
FEMALE_NAMES = ["마리아", "소피아", "하나", "엘라", "니나", "야나", "이리나", "에바", "릴리", "클라라", "미아", "아이다", "레나", "사라", "유나"]
SURNAMES = ["볼코프", "하르트만", "모레노", "카미야", "올센", "로시", "칼리노", "베르크", "아사노", "노박", "실바", "린드", "코바치", "파렐", "드보르", "마르틴", "에크", "야코비", "소렌센", "벨로", "아두", "케인", "오르테가", "스텐"]

# 한국어 표기: (영어 프롬프트용, SVG 색)
EYE_COLORS = {
    "갈색": ("brown", "#6b3e1f"),
    "검정": ("black", "#1a1a1a"),
    "파랑": ("blue", "#2f6fd6"),
    "초록": ("green", "#2e8b57"),
    "회색": ("grey", "#8a96a3"),
}
HAIR_COLORS = {
    "검정": ("black", "#1f1b18"),
    "갈색": ("brown", "#6b4226"),
    "금발": ("blond", "#d9b45a"),
    "빨강": ("red", "#a8432a"),
    "회색": ("grey", "#a0a0a0"),
}
# 한국어 표기 → (그리기 키, 영어 프롬프트)
HAIR_STYLES = {
    "짧은 머리": ("short", "short"),
    "옆가르마": ("sidepart", "side-parted short"),
    "긴 머리": ("long", "long straight"),
    "단발": ("bob", "bob-cut"),
    "곱슬 머리": ("curly", "curly"),
    "삭발": ("shaved", "buzz-cut"),
    "묶은 머리": ("ponytail", "ponytail"),
    "올림머리": ("bun", "bun"),
    "대머리": ("balding", "balding"),
}
# 성별별 헤어스타일 가중치 (어느 성별이든 대부분 가능)
HAIR_WEIGHTS = {
    "M": {"짧은 머리": 5, "옆가르마": 4, "곱슬 머리": 2, "삭발": 3, "긴 머리": 1, "묶은 머리": 1, "대머리": 2},
    "F": {"긴 머리": 5, "단발": 4, "묶은 머리": 3, "올림머리": 2, "곱슬 머리": 2, "짧은 머리": 2, "삭발": 1},
}

# 피부톤은 인종 카테고리가 아니라 연속 범위에서 보간해 뽑는다.
SKIN_STOPS = ["#f7dcc9", "#efc4a2", "#dfa67c", "#c68a5e", "#a36c46", "#7e5034", "#5a3824", "#3f271a"]

# 얼굴 파라미터 (특정 인물을 재현하지 않도록 조합형으로 생성)
FACE_SHAPES = {"oval": "oval", "round": "round", "square": "square-jawed", "long": "long", "heart": "heart-shaped"}
NOSES = {"small": "small nose", "straight": "straight nose", "wide": "broad nose", "hooked": "aquiline nose", "button": "button nose"}
LIPS = {"thin": "thin lips", "medium": "medium lips", "full": "full lips"}
BROWS = {"thin": "thin eyebrows", "medium": "", "thick": "thick eyebrows", "arched": "arched eyebrows"}
EYE_SIZES = {"small": "small eyes", "normal": "", "large": "large eyes"}
EARS = {"small": 3.2, "normal": 4.0, "large": 5.2}

# 얼굴·목처럼 겉으로 보이는 특징 (생체 스캔으로 확인)
VISIBLE_MARKS = {
    "왼쪽 뺨 흉터": "a scar on the left cheek",
    "오른쪽 뺨 흉터": "a scar on the right cheek",
    "눈썹 흉터": "a scar through the eyebrow",
    "턱 흉터": "a scar on the chin",
    "코 옆 점": "a mole beside the nose",
    "목 장미 문신": "a small rose tattoo on the neck",
}
# 옷에 가려진 특징 (몸수색으로만 확인)
HIDDEN_MARKS = {
    "등 용 문신": "dragon tattoo on the back",
    "팔뚝 닻 문신": "anchor tattoo on the forearm",
    "가슴 전갈 문신": "scorpion tattoo on the chest",
    "어깨 해골 문신": "skull tattoo on the shoulder",
    "손목 바코드 문신": "barcode tattoo on the wrist",
}

TOPS = {
    "트렌치코트": ("trench coat", "coat"),
    "패딩 점퍼": ("puffer jacket", "coat"),
    "후드티": ("hoodie", "hoodie"),
    "정장 재킷": ("suit jacket", "jacket"),
    "티셔츠": ("t-shirt", "tee"),
    "셔츠": ("button-up shirt", "tee"),
}
BULKY_TOPS = ["트렌치코트", "패딩 점퍼", "후드티"]
BOTTOMS = {
    "청바지": ("jeans", "long"),
    "정장 바지": ("dress trousers", "long"),
    "카고 바지": ("cargo pants", "long"),
    "반바지": ("shorts", "short"),
}
CLOTH_COLORS = {
    "검정": ("black", "#2b2b2b"),
    "회색": ("grey", "#7d7d7d"),
    "남색": ("navy", "#27365e"),
    "베이지": ("beige", "#c8b28a"),
    "카키": ("khaki", "#6f7045"),
    "빨강": ("red", "#a83232"),
    "하양": ("white", "#e9e9e9"),
    "갈색": ("brown", "#6e4a2f"),
    "하늘": ("light blue", "#7fb3d5"),
}
HATS = {
    None: None,
    "야구모자": "baseball cap",
    "비니": "beanie",
    "페도라": "fedora",
}
LUGGAGE_COLORS = {
    "검정": ("black", "#303030"),
    "빨강": ("red", "#b03030"),
    "은색": ("silver", "#b8bec6"),
    "남색": ("navy", "#2c3e6b"),
    "노랑": ("yellow", "#d6a826"),
}

PURPOSES = ["관광", "출장", "친척 방문", "유학", "취업"]
LODGINGS = ["시내 호텔", "친척 집", "학교 기숙사", "회사 숙소", "게스트하우스"]
JOBS = ["회사원", "학생", "교사", "엔지니어", "요리사", "간호사", "자영업자", "디자이너", "은퇴자", "기자"]
NO_VISA_MAX_DAYS = 30

# 소지품. danger: None / "drug" / "weapon" / "explosive"
# xray: X-ray 도형 종류
LUGGAGE_SAFE = [
    ("옷가지", "clothes"),
    ("신발", "shoes"),
    ("노트북", "laptop"),
    ("세면도구", "toiletry"),
    ("책", "book"),
    ("카메라", "camera"),
    ("충전기", "charger"),
    ("우산", "umbrella"),
    ("물병", "bottle"),
    ("기념품 인형", "doll"),
]
LUGGAGE_DANGER = {
    "drug": [("마약 벽돌", "drug")],
    "weapon": [("권총", "pistol"), ("칼", "knife"), ("탄약", "ammo")],
    "explosive": [("시한폭탄", "bomb")],
}
# (이름, 금속 여부, 부위)
BODY_SAFE = [
    ("벨트 버클", True, "허리"),
    ("열쇠 꾸러미", True, "주머니"),
    ("동전", True, "주머니"),
    ("손목시계", True, "손목"),
    ("손수건", False, "주머니"),
    ("껌", False, "주머니"),
]
BODY_BULGE_SAFE = ("두툼한 지갑", False, "코트 안쪽")
BODY_DANGER = {
    "drug": [("마약 봉지", False, "코트 안쪽")],
    "weapon": [("권총", True, "허리"), ("접이식 칼", True, "발목")],
    "explosive": [("폭발물 조끼", True, "몸통")],
}
BODY_ZONES = ["머리", "몸통", "코트 안쪽", "허리", "손목", "주머니", "발목"]

CRIMES = [
    ("무장 강도", False),
    ("마약 밀매", False),
    ("금융 사기", False),
    ("살인 미수", False),
    ("테러 모의", True),
    ("폭탄 테러 용의", True),
]

# 규칙 코드 → (이름, 올바른 조치, 설명)
RULES = {
    "EXPIRED": ("여권 만료", "DENY", "여권 유효기간이 오늘 날짜 이전이면 입국 거부."),
    "SEAL": ("도장 위조", "ARREST", "여권 도장 색이 발급국 공식 색과 다르면 위조 여권 → 체포."),
    "PHOTO": ("본인 불일치", "ARREST", "성별·눈동자 색·특이사항이 여권과 다르거나 키가 7cm 넘게 차이 나면 신분 도용 → 체포. (머리색·안경·수염은 바뀔 수 있으므로 기준이 아님)"),
    "WANTED": ("수배자", "ARREST", "여권 이름이 수배자와 같거나, 성별·눈동자 색·특이사항(흉터·문신)이 수배자와 모두 같으면 체포."),
    "VISA": ("비자 문제", "DENY", "비자 필요 국가 국민은 유효한 비자 필요. 비자의 이름·여권번호가 여권과 같아야 하고 만료되지 않아야 함."),
    "INTERVIEW": ("진술 불일치", "DENY", f"인터뷰의 방문 목적이 비자와 달라도, 체류 기간이 비자 허용일(무비자는 {NO_VISA_MAX_DAYS}일)을 넘어도 입국 거부. 자국민은 해당 없음."),
    "CONTRABAND": ("마약 소지", "ARREST", "캐리어나 몸에서 마약이 나오면 체포."),
    "WEAPON": ("무기·폭발물", "ARREST", "총기·칼·탄약·폭발물 소지 시 체포. 폭발물은 테러 용의자."),
    "PASSPORT_NO": ("여권번호 위조", "ARREST", "여권번호는 '발급국 코드-숫자 7자리' 형식이어야 함. 다르면 위조 → 체포."),
}

# 스토리 모드: 날짜별로 새로 추가되는 규칙
DAY_NEW_RULES = {
    1: ["EXPIRED", "SEAL", "PHOTO"],
    2: ["WANTED"],
    3: ["VISA", "INTERVIEW"],
    4: ["CONTRABAND", "WEAPON"],
    5: ["PASSPORT_NO"],
}
STORY_DAYS = len(DAY_NEW_RULES)
ALL_RULES = [r for day in sorted(DAY_NEW_RULES) for r in DAY_NEW_RULES[day]]


def rules_for_day(day: int) -> list[str]:
    return [r for d in sorted(DAY_NEW_RULES) if d <= day for r in DAY_NEW_RULES[d]]


# 도구 사용 시 소모되는 게임 시간(분). 스토리 모드에서만 적용.
TOOL_MINUTES = {"scan": 1, "question": 1, "xray": 3, "metal": 2, "search": 5}
BASE_MINUTES = 3
SHIFT_START = 9 * 60
SHIFT_END = 11 * 60
ENDLESS_SECONDS = 300
ENDLESS_LIVES = 3
