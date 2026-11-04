"""Demo data. Run from the folder that contains backend/:

    python -m backend.seed            # insert 30 sample visits
    python -m backend.seed --clear    # delete ALL rows
"""
import random
import sys
from datetime import timedelta

from core.database import Base, SessionLocal, engine
from models import Visit
from models.visit import utcnow

Base.metadata.create_all(bind=engine)

DEVICES = [
    ("Chrome", "130", "Android", "14", "mobile"),
    ("Safari", "18", "iOS", "18.0", "mobile"),
    ("Chrome", "130", "Windows", "11", "desktop"),
    ("Firefox", "132", "Linux", "", "desktop"),
    ("Safari", "18", "Mac OS X", "14.5", "desktop"),
    ("Chrome", "130", "Android", "13", "tablet"),
    ("Googlebot", "2", "Other", "", "bot"),
]
PLACES = [
    ("Nigeria", "Rivers", "Port Harcourt"),
    ("Nigeria", "Lagos", "Lagos"),
    ("Nigeria", "Federal Capital Territory", "Abuja"),
    ("Ghana", "Greater Accra", "Accra"),
    ("United Kingdom", "England", "London"),
    ("United States", "California", "San Francisco"),
    (None, None, None),
]


def main() -> None:
    db = SessionLocal()
    try:
        if "--clear" in sys.argv:
            n = db.query(Visit).delete()
            db.commit()
            print(f"Deleted {n} rows")
            return
        now = utcnow()
        for _ in range(30):
            b, bv, o, ov, d = random.choice(DEVICES)
            c, r, ci = random.choice(PLACES)
            db.add(Visit(
                visited_at=now - timedelta(minutes=random.randint(1, 60 * 72)),
                page_path=random.choice(["/", "/", "/about", "/pricing"]),
                ip_address=f"{random.randint(41, 197)}.{random.randint(0, 255)}.0.0",
                browser_name=b, browser_version=bv, os_name=o, os_version=ov or None,
                device_type=d, country=c, region=r, city=ci,
            ))
        db.commit()
        print("Inserted 30 sample visits")
    finally:
        db.close()


if __name__ == "__main__":
    main()
