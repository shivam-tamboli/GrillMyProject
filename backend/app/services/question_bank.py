import json
import random
from pathlib import Path

_BANK_PATH = Path(__file__).resolve().parent.parent / "data" / "question_bank.json"

with open(_BANK_PATH, encoding="utf-8") as f:
    BANK: dict[str, list[dict]] = json.load(f)


def pick_questions(level: str, seen_ids: list[str] | None = None, count: int | None = None) -> list[dict]:
    """Intro first, then 3 or 4 random questions from the level's pool.

    seen_ids are the bank ids this user has been asked before, oldest first.
    Unseen questions are used first. If there are not enough, the rest come
    from the seen ones, longest ago first.
    """
    pool = BANK.get(level)
    if pool is None:
        raise ValueError(f"unknown level: {level}")

    intro_id = f"{level}-intro"
    intro = next(q for q in pool if q["id"] == intro_id)
    rest = [q for q in pool if q["id"] != intro_id]

    n = count if count is not None else random.choice([3, 4])
    n = min(n, len(rest))

    # a question seen twice counts from the last time it was asked
    last_seen = {qid: i for i, qid in enumerate(seen_ids or [])}

    unseen = [q for q in rest if q["id"] not in last_seen]
    picked = random.sample(unseen, min(n, len(unseen)))

    if len(picked) < n:
        seen = sorted((q for q in rest if q["id"] in last_seen), key=lambda q: last_seen[q["id"]])
        picked += seen[: n - len(picked)]

    return [dict(intro)] + [dict(q) for q in picked]
