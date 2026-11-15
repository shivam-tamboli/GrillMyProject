# Rules match SYSTEM_DESIGN.md, Section 2 (phases by time, dynamic difficulty).
LEVEL_ORDER = ("easy", "medium", "hard")

RESUME_END = 15
BEHAVIORAL_END = 25
SESSION_MINUTES = 45

UPGRADE_SCORE = 7
UPGRADE_STREAK = 3


def phase_for(elapsed_minutes: float) -> str:
    """Phase for the time since the session started.

    Returns the question_type used on messages (resume, behavioral, technical),
    or "ended" once the 45 minutes are over.
    """
    if elapsed_minutes < 0:
        raise ValueError("elapsed_minutes is negative")
    if elapsed_minutes < RESUME_END:
        return "resume"
    if elapsed_minutes < BEHAVIORAL_END:
        return "behavioral"
    if elapsed_minutes < SESSION_MINUTES:
        return "technical"
    return "ended"


def after_score(level: str, streak: int, score: int) -> tuple[str, int]:
    """Apply one score to the difficulty rule. Returns (level, streak).

    A score of 7 or more adds to the streak, anything lower resets it. On the
    third in a row the level goes up one step and the streak starts again from
    zero. Hard has no step above it, so it stays hard.
    """
    if level not in LEVEL_ORDER:
        raise ValueError(f"unknown level: {level}")

    streak = streak + 1 if score >= UPGRADE_SCORE else 0
    if streak >= UPGRADE_STREAK:
        next_index = min(LEVEL_ORDER.index(level) + 1, len(LEVEL_ORDER) - 1)
        return LEVEL_ORDER[next_index], 0
    return level, streak
