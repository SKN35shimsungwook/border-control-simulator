import random
from datetime import timedelta

from game import data as D
from game.engine import Game
from game.generator import make_traveler, make_wanted_list
from game.rules import expected_action, find_violations


def test_checker_finds_exactly_the_injected_flaws():
    rng = random.Random(1234)
    for day in range(1, D.STORY_DAYS + 1):
        rules = D.rules_for_day(day)
        today = D.START_DATE + timedelta(days=day - 1)
        for _ in range(40):
            wanted = make_wanted_list(rng, 4) if "WANTED" in rules else []
            for i in range(25):
                t = make_traveler(rng, i, today, rules, wanted, p_bad=0.6)
                found = find_violations(t, rules, today, wanted)
                assert set(found) == set(t.flaws), (day, t.flaws, found, t)


def test_clean_travelers_are_approved():
    rng = random.Random(7)
    rules = D.ALL_RULES
    wanted = make_wanted_list(rng, 4)
    for i in range(300):
        t = make_traveler(rng, i, D.START_DATE, rules, wanted, p_bad=0.0)
        assert expected_action(find_violations(t, rules, D.START_DATE, wanted)) == "APPROVE"


def test_story_game_runs_to_the_end():
    g = Game.new("story", seed=3)
    while g.phase != "over":
        if g.phase == "briefing":
            g.start_shift()
        elif g.phase == "inspect":
            g.use_tool("scan")
            g.decide(g.truth()["action"], g.truth()["violations"])
        elif g.phase == "day_end":
            g.next_day()
    assert g.day == D.STORY_DAYS
    assert g.correct == len(g.log)
    assert g.score > 0


def test_endless_game_loses_lives():
    g = Game.new("endless", seed=5)
    g.start_shift()
    while g.phase == "inspect":
        g.decide("APPROVE", [])
    assert g.lives == 0
