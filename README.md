# 국경 심사관 (Border Control Simulator)

입국자의 여권·비자·인상착의·복장·캐리어를 검사해서 **입국 승인 / 입국 거부 / 체포** 중 하나를 결정하는 Streamlit 게임입니다.
테러리스트와 수배자를 걸러낼수록 점수가 올라갑니다.

## 실행

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 게임 구성

| 요소 | 내용 |
|---|---|
| 모드 | **스토리**: Day 1–5, 날마다 규칙이 추가됨. 근무 시간(09:00–11:00)이 있어서 도구를 쓸 때마다 게임 시간이 줄어듦<br>**무한**: 모든 규칙 적용, 실제 시간 5분, 목숨 3개 |
| 서류 | 여권(사진·도장 색·번호 형식·만료일·신체 특징), 비자(이름·여권번호·목적·체류일·유효기간) |
| 검사 도구 | 인터뷰, 생체 스캔(눈동자·키·특이사항), 캐리어 X-ray, 금속탐지기, 몸수색(숨긴 물건·가려진 문신) |
| 위협 | 위조 여권, 신분 도용, 수배자(가명 사용 포함), 마약, 총기·칼·폭발물(테러) |
| 점수 | 정답 판정, 위반 사유를 정확히 고르면 보너스, 테러범 체포 시 큰 보너스, 위험인물 입국 시 큰 감점 |
| 리더보드 | `data/leaderboard.db` (SQLite) |

모든 국가는 가상 국가이며, 범죄자·테러리스트 배정은 국적이나 외모와 관계없이 무작위입니다.

## 캐릭터

실존 인물을 재현하지 않도록 **조합형으로 새로 생성**합니다.

- 얼굴형 5 × 코 5 × 입술 3 × 눈썹 4 × 눈 크기 3 × 귀 3, 나이 주름·주근깨·보조개, 헤어스타일 9종
- 피부톤은 인종 카테고리가 아니라 연속 범위에서 보간해 뽑습니다.
- 앱의 **입국자 갤러리** 메뉴에서 생성 결과를 한눈에 볼 수 있습니다.
- MakeHuman/Blender 등으로 만든 PNG 파츠를 `assets/parts/` 에 넣으면 그 부위만 교체됩니다. 방법은 [assets/README.md](assets/README.md) 참고.

## 이미지

기본값은 코드로 그리는 **SVG 일러스트**라서 API 키 없이 동작합니다.
`.streamlit/secrets.toml`(또는 Streamlit Cloud의 Secrets)에 아래 키 중 하나를 넣으면 입국자 전신·여권 사진을 AI 이미지로 바꿉니다.

```toml
POLLINATIONS_API_KEY = "..."   # https://enter.pollinations.ai 에서 발급
# 또는
OPENAI_API_KEY = "sk-..."
OPENAI_IMAGE_MODEL = "gpt-image-1"  # 선택
```

- Pollinations의 키 없는 무료 엔드포인트는 현재 결제를 요구(HTTP 402)해서 키가 있어야 합니다.
- 이미지는 서버의 백그라운드 스레드가 받아 오기 때문에 키가 브라우저에 노출되지 않습니다. 생성 중이거나 실패하면 SVG를 보여 줍니다.
- AI 이미지는 같은 사람을 매번 똑같이 그리지 못합니다. 그래서 본인 확인 판정은 사진이 아니라 **생체 스캔 수치(눈동자 색·키·특이사항)와 여권 기재 내용을 비교**하는 방식으로 되어 있습니다.
- X-ray·금속탐지기 화면은 판정 근거가 되어야 하므로 항상 SVG로 그립니다.

## 코드 구조

```
streamlit_app.py        # 진입점, st.navigation
app_pages/
  play.py               # 메뉴 → 브리핑 → 심사 → 하루 종료 → 평가
  manual.py             # 근무 수칙
  gallery.py            # 입국자 갤러리
  leaderboard.py        # 리더보드
game/
  data.py               # 국가, 특징, 복장, 소지품, 규칙, 날짜별 규칙
  models.py             # Person / Passport / Visa / Item / Traveler / WantedEntry
  generator.py          # 입국자·수배자 생성 (결함을 일부러 심음)
  rules.py              # 판정 기준 (생성기와 독립적으로 위반 사항 계산)
  scoring.py            # 점수표, 등급
  engine.py             # 게임 진행 상태 (Streamlit 비의존)
  art.py                # SVG 일러스트 (조합형 얼굴)
  parts.py              # 선택형 PNG 파츠 레이어
  ai_images.py          # 선택형 AI 이미지 (Pollinations / OpenAI)
  ui.py                 # 여권·비자 카드, 수배자 카드, 수칙 렌더링
  leaderboard.py        # SQLite
tools/
  make_part_guides.py   # PNG 파츠 정렬 가이드 생성
assets/                 # PNG 파츠 슬롯 + 가이드
tests/test_generator.py # 생성기가 심은 결함 = 판정기가 찾은 위반인지 검증
```

## 테스트

```bash
python -m pytest tests
```

## 배포 (Streamlit Community Cloud)

메인 파일 경로를 `streamlit_app.py`로 지정합니다. Community Cloud의 파일 시스템은 영구 저장이 아니어서 앱이 재시작되면 리더보드가 초기화될 수 있습니다.
