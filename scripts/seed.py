"""Seed a large, realistic `users` collection for explain-plan experiments.

    python scripts/seed.py            # default: 50,000 docs
    python scripts/seed.py 200000     # custom count

Why a *big* collection? With only a handful of documents, a collection scan
(COLLSCAN) and an index scan (IXSCAN) both examine ~all the docs in ~0ms, so
Compass's Explain Plan tab shows no interesting difference. With tens of
thousands of docs the story becomes obvious: COLLSCAN examines *everything*
while IXSCAN examines a handful.

This script inserts data ONLY -- it deliberately creates no secondary indexes
so the starting state is a clean COLLSCAN on every field (great for "before"
screenshots). Add indexes afterwards from Compass or via `explain_demo.py`.

Uses only the standard library (`random`, `datetime`) plus pymongo -- no
data-faker dependency, per the project's "strictly-needed deps only" rule.
"""
import random
import sys
from datetime import datetime, timedelta

from db import get_db

# Fixed seed -> the exact same 50k docs every run, so your screenshots and
# document counts are reproducible.
random.seed(42)

COLLECTION = "users"

FIRST_NAMES = [
    "Ada", "Grace", "Alan", "Katherine", "Linus", "Margaret", "Dennis",
    "Barbara", "Ken", "Radia", "Tim", "Hedy", "Guido", "Anita", "James",
    "Shafi", "Vint", "Frances", "Donald", "Adele",
]
LAST_NAMES = [
    "Lovelace", "Hopper", "Turing", "Johnson", "Torvalds", "Hamilton",
    "Ritchie", "Liskov", "Thompson", "Perlman", "Berners-Lee", "Lamarr",
    "Rossum", "Borg", "Gosling", "Goldwasser", "Cerf", "Allen", "Knuth",
    "Goldberg",
]
CITIES = [
    "Istanbul", "Berlin", "London", "New York", "Tokyo", "Paris",
    "Amsterdam", "Toronto", "Singapore", "Sydney",
]
COUNTRIES = ["TR", "DE", "UK", "US", "JP", "FR", "NL", "CA", "SG", "AU"]
ROLES = ["engineer", "researcher", "designer", "manager", "analyst"]

# Weighted so `status` has low cardinality with a dominant value -- this makes
# selectivity differences visible in explain (most docs are "active").
STATUSES = ["active"] * 6 + ["inactive"] * 2 + ["pending"] + ["banned"]

# Sign-up dates spread across ~4 years, so sorting by date is meaningful.
START_DATE = datetime(2022, 1, 1)
DATE_SPAN_DAYS = 4 * 365


def make_doc(i: int) -> dict:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return {
        "user_id": i,  # unique, sequential -- good for range/covered demos
        "name": f"{first} {last}",
        # Email is high-cardinality (unique per doc) -> perfect COLLSCAN vs
        # IXSCAN example: an equality match returns exactly one document.
        "email": f"{first}.{last}.{i}@example.com".lower(),
        "age": random.randint(18, 80),
        "status": random.choice(STATUSES),
        "city": random.choice(CITIES),
        "country": random.choice(COUNTRIES),
        "role": random.choice(ROLES),
        "score": random.randint(0, 1000),
        "signup_date": START_DATE
        + timedelta(days=random.randint(0, DATE_SPAN_DAYS)),
    }


def main() -> None:
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 50_000
    users = get_db()[COLLECTION]

    print(f"Dropping and reseeding `{COLLECTION}` with {count:,} documents...")
    users.drop()  # drop (not delete_many) so old indexes go too -> clean slate

    batch, batch_size = [], 5_000
    for i in range(count):
        batch.append(make_doc(i))
        if len(batch) == batch_size:
            users.insert_many(batch, ordered=False)
            batch.clear()
            print(f"  inserted {i + 1:,} / {count:,}", end="\r")
    if batch:
        users.insert_many(batch, ordered=False)

    total = users.count_documents({})
    print(f"\nDone. `{COLLECTION}` now has {total:,} documents.")
    print("Indexes (only the default _id_ for now):")
    for name in users.index_information():
        print(f"  {name}")
    print(
        "\nNext: open Compass -> playground.users, or run "
        "`python scripts/explain_demo.py`."
    )


if __name__ == "__main__":
    main()
