from __future__ import annotations
import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Dict, Tuple

# --- Config you can tune later ---
MEMORY_THRESHOLD = 0.65  # schedule a review when memory drops below this

# decay rate (k) by difficulty 1–5
K_BY_DIFFICULTY = {
    1: 0.10,
    2: 0.13,
    3: 0.16,
    4: 0.20,
    5: 0.25,
}

@dataclass
class Topic:
    subject: str
    name: str
    difficulty: int             # 1–5
    last_revised: date          # last time revised
    est_minutes: int            # typical session length (e.g., 20–45)
    revision_count: int = 0     # increases each time it's scheduled

def parse_uk_date(d: str) -> date:
    """Parses dd-mm-yyyy (UK style). Example: '01-06-2026'."""
    return datetime.strptime(d, "%d-%m-%Y").date()

def memory_score(days_since: int, difficulty: int, revision_count: int) -> float:
    """
    Memory(t) = e^(-k * days)
    Spaced repetition effect: as revision_count increases, decay slows slightly.
    """
    base_k = K_BY_DIFFICULTY[difficulty]
    k = base_k * (0.90 ** revision_count)  # each revision slows decay ~10%
    return math.exp(-k * max(0, days_since))

def daily_stress_minutes_limit(minutes_available: int, sleep_hours: float) -> int:
    """
    Simple burnout cap: if you sleep less, the system schedules less.
    (Keeps it explainable + not 'AI'.)
    """
    sleep_factor = max(0.6, min(1.1, sleep_hours / 8.0))  # clamp
    return int(minutes_available * sleep_factor)

def build_plan(
    topics: List[Topic],
    exam_date: date,
    minutes_available_per_day: int,
    sleep_hours: float,
    start_date: date | None = None
) -> Tuple[Dict[date, List[Topic]], Dict[date, int]]:
    """
    Returns:
      plan[day] = list of scheduled Topic objects for that day
      minutes_used[day] = total minutes scheduled that day
    """
    if start_date is None:
        start_date = date.today()

    if exam_date < start_date:
        raise ValueError("Exam date is in the past relative to start_date.")

    plan: Dict[date, List[Topic]] = {}
    minutes_used: Dict[date, int] = {}

    days_total = (exam_date - start_date).days + 1

    for i in range(days_total):
        day = start_date + timedelta(days=i)
        plan[day] = []
        minutes_used[day] = 0

        cap = daily_stress_minutes_limit(minutes_available_per_day, sleep_hours)

        # Priority: lowest memory first, then higher difficulty, then longer since revised
        scored = []
        for t in topics:
            days_since = (day - t.last_revised).days
            mem = memory_score(days_since, t.difficulty, t.revision_count)
            scored.append((mem, -t.difficulty, -days_since, t))

        scored.sort(key=lambda x: (x[0], x[1], x[2]))  # lowest mem first

        for mem, _, _, t in scored:
            if mem >= MEMORY_THRESHOLD:
                continue  # not urgent yet

            if minutes_used[day] + t.est_minutes > cap:
                continue  # protect against overload

            # schedule it
            plan[day].append(t)
            minutes_used[day] += t.est_minutes

            # update topic state as if revised on this day
            t.last_revised = day
            t.revision_count += 1

        # Optional: add a light “maintenance” slot close to exam
        # (You can add later—keep MVP simple.)

    return plan, minutes_used
