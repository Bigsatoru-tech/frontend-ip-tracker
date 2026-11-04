import os

# Settings are read when the app is imported, so set these BEFORE importing it.
os.environ["DATABASE_URL"] = "sqlite:///./test_visits.db"
os.environ["APP_ENV"] = "dev"
os.environ["ADMIN_KEY"] = "testkey"
os.environ["GEOIP_DB_PATH"] = "./does-not-exist.mmdb"

from fastapi.testclient import TestClient  # noqa: E402

from core.tracker import analyze, truncate_ip  # noqa: E402
from main import app  # noqa: E402

ANDROID = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36")
DESKTOP = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
BOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

client = TestClient(app)


def test_truncate():
    assert truncate_ip("102.89.45.7") == "102.89.0.0"
    assert truncate_ip("not-an-ip") is None
    assert truncate_ip(None) is None


def test_user_agents():
    assert analyze("102.89.45.7", ANDROID).device_type == "mobile"
    assert analyze("102.89.45.7", ANDROID).os_name == "Android"
    assert analyze("102.89.45.7", DESKTOP).device_type == "desktop"
    assert analyze("102.89.45.7", BOT).device_type == "bot"
    assert analyze(None, None).device_type == "unknown"


def test_local_ip_has_no_location():
    a = analyze("127.0.0.1", DESKTOP)
    assert a.country is None and a.city is None


def test_visit_saved_and_listed():
    r = client.post("/api/visit", json={"page_path": "/x?token=secret"},
                    headers={"User-Agent": ANDROID, "X-Debug-IP": "102.89.45.7"})
    assert r.status_code == 200
    body = r.json()
    assert body["ip_address"] == "102.89.0.0"
    assert body["device"] == "Mobile"
    assert body["location"] == "Unknown"  # no GeoIP file in tests

    rows = client.get("/api/visits", headers={"X-API-Key": "testkey"}).json()
    assert rows[0]["page_path"] == "/x"  # query string removed
    assert rows[0]["ip_address"] == "102.89.0.0"


def test_list_requires_key():
    assert client.get("/api/visits").status_code == 401
    assert client.get("/api/visits", headers={"X-API-Key": "wrong"}).status_code == 401
