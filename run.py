from datetime import date
from engine import Topic, parse_uk_date, build_plan

EXAM_DATE = parse_uk_date("01-06-2026")

# Replace these with YOUR real topics (start with ~10–20)
topics = [
    Topic("Maths", "Simultaneous equations", 4, date(2025, 12, 28), 30),
    Topic("English", "Violence in Shakespeare", 3, date(2025, 12, 30), 25),
    Topic("Chemistry", "Ionic bonding", 4, date(2025, 12, 27), 30),
    Topic("Biology", "Active transport", 3, date(2025, 12, 29), 25),
    Topic("Physics", "Forces", 4, date(2025, 12, 26), 30),
    Topic("Maths", "Fractions basics", 2, date(2025, 12, 31), 20),
    Topic("English", "PEEL paragraphs", 2, date(2025, 12, 31), 20),
    Topic("Chemistry", "Atoms & isotopes", 2, date(2025, 12, 25), 20),
    Topic("Biology", "Diffusion & osmosis", 2, date(2025, 12, 24), 20),
    Topic("Physics", "Speed/distance/time", 2, date(2025, 12, 23), 20),
]

minutes_per_day = 60          # change this
sleep_hours = 8.0             # change this

plan, minutes_used = build_plan(
    topics=topics,
    exam_date=EXAM_DATE,
    minutes_available_per_day=minutes_per_day,
    sleep_hours=sleep_hours,
    start_date=date(2026, 1, 3)  # lock to today for consistency
)

# Print the first 14 days so you can sanity-check it
days = sorted(plan.keys())[:14]
for d in days:
    items = plan[d]
    print(f"\n{d}  | {minutes_used[d]} min")
    if not items:
        print("  (Rest / no urgent reviews)")
    else:
        for t in items:
            print(f"  - {t.subject}: {t.name} (diff {t.difficulty}, {t.est_minutes}m)")
