"""게임 진행 상태. Streamlit과 무관하게 동작하므로 테스트 가능하다."""

import random
import time
from dataclasses import dataclass, field
from datetime import date, timedelta

from . import data as D
from .generator import make_traveler, make_wanted_list
from .models import Traveler, WantedEntry
from .rules import expected_action, find_violations, is_terrorist
from .scoring import score_decision

# phase: "briefing" → "inspect" → ("day_end" → "briefing" ...) → "over"


@dataclass
class Game:
    mode: str  # "story" / "endless"
    seed: int
    rng: random.Random
    day: int = 1
    rules: list[str] = field(default_factory=list)
    today: date = D.START_DATE
    wanted: list[WantedEntry] = field(default_factory=list)
    new_rules: list[str] = field(default_factory=list)
    phase: str = "briefing"
    clock: int = D.SHIFT_START
    score: int = 0
    lives: int = D.ENDLESS_LIVES
    started_at: float | None = None
    current: Traveler | None = None
    revealed: set = field(default_factory=set)
    asked: list = field(default_factory=list)
    log: list = field(default_factory=list)
    day_start: int = 0
    next_id: int = 1
    last_feedback: dict | None = None
    saved: bool = False

    @classmethod
    def new(cls, mode: str, seed: int | None = None) -> "Game":
        seed = seed if seed is not None else random.randrange(1, 10**9)
        g = cls(mode=mode, seed=seed, rng=random.Random(seed))
        g._setup_day()
        return g

    # ---- 진행 ----
    def _setup_day(self):
        if self.mode == "story":
            self.rules = D.rules_for_day(self.day)
            self.new_rules = D.DAY_NEW_RULES[self.day]
            self.today = D.START_DATE + timedelta(days=self.day - 1)
        else:
            self.rules = D.ALL_RULES[:]
            self.new_rules = D.ALL_RULES[:]
            self.today = D.START_DATE
        n_wanted = 4 if self.mode == "endless" else 3
        self.wanted = make_wanted_list(self.rng, n_wanted) if "WANTED" in self.rules else []
        self.clock = D.SHIFT_START
        self.day_start = len(self.log)
        self.phase = "briefing"

    def start_shift(self):
        self.phase = "inspect"
        if self.mode == "endless":
            self.started_at = time.time()
        self._next_traveler()

    def _p_bad(self) -> float:
        if self.mode == "story":
            return 0.35 + 0.04 * self.day
        return min(0.65, 0.4 + 0.01 * len(self.log))

    def _next_traveler(self):
        self.current = make_traveler(self.rng, self.next_id, self.today, self.rules, self.wanted, self._p_bad())
        self.next_id += 1
        self.revealed = set()
        self.asked = []

    def _spend(self, minutes: int):
        if self.mode == "story":
            self.clock += minutes

    def use_tool(self, tool: str):
        if tool not in self.revealed:
            self.revealed.add(tool)
            self._spend(D.TOOL_MINUTES[tool])

    def ask(self, question: str):
        if question not in self.asked:
            self.asked.append(question)
            self._spend(D.TOOL_MINUTES["question"])

    def truth(self) -> dict:
        t = self.current
        violations = find_violations(t, self.rules, self.today, self.wanted)
        return {
            "violations": violations,
            "action": expected_action(violations),
            "terrorist": is_terrorist(t, violations, self.wanted),
        }

    def decide(self, action: str, reasons: list[str]):
        t, truth = self.current, self.truth()
        result = score_decision(truth["action"], action, truth["terrorist"], reasons, truth["violations"])
        self.score += result["points"]
        if self.mode == "endless" and result["severe"]:
            self.lives -= 1
        entry = {
            "day": self.day,
            "name": t.passport.name,
            "nationality": t.person.nationality,
            "action": action,
            "expected": truth["action"],
            "violations": truth["violations"],
            "terrorist": truth["terrorist"],
            **result,
        }
        self.log.append(entry)
        self.last_feedback = entry
        self._spend(D.BASE_MINUTES)

        if self.mode == "endless":
            if self.lives <= 0 or self.time_left() <= 0:
                self.phase = "over"
                return
        elif self.clock >= D.SHIFT_END:
            self.phase = "day_end"
            return
        self._next_traveler()

    def next_day(self):
        if self.mode == "endless" or self.day >= D.STORY_DAYS:
            self.phase = "over"
            return
        self.day += 1
        self._setup_day()

    def time_left(self) -> float:
        if self.mode != "endless" or self.started_at is None:
            return float(D.ENDLESS_SECONDS)
        return D.ENDLESS_SECONDS - (time.time() - self.started_at)

    def check_timeout(self) -> bool:
        if self.mode == "endless" and self.phase == "inspect" and self.time_left() <= 0:
            self.phase = "over"
            return True
        return False

    # ---- 통계 ----
    @property
    def correct(self) -> int:
        return sum(e["correct"] for e in self.log)

    @property
    def accuracy(self) -> float:
        return self.correct / len(self.log) if self.log else 0.0

    def day_entries(self) -> list[dict]:
        return self.log[self.day_start :]

    def clock_text(self) -> str:
        return f"{self.clock // 60:02d}:{self.clock % 60:02d}"
