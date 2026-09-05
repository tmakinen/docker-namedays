import json
import sys
import urllib.error
import urllib.request
import zoneinfo
from datetime import datetime

TIMEZONE = zoneinfo.ZoneInfo("Europe/Helsinki")


def fetch_api(base_url, endpoint):
    """Helper to handle urllib requests and return (status_code, json_dict or None)."""
    url = f"{base_url}{endpoint}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            body = response.read().decode("utf-8")
            return response.getcode(), json.loads(body)
    except urllib.error.HTTPError as e:
        return e.code, None


def verify_success_payload(data):
    """Validates presence and structural accuracy of grocery hours data."""
    assert data is not None, "Expected JSON response body, got None"
    keys = [
        "hevonen",
        "historiallinen",
        "kissa",
        "koira",
        "ortod",
        "ruotsi",
        "saame",
        "suomi",
    ]
    for k in keys:
        assert k in data, f"Missing required '{k}' key in payload: {data}"
    for k in data:
        assert k in keys, f"Unknown key '{k}' in payload: {data}"


def test_api_routes(base_url):
    # 1. Setup dynamic test dates
    today_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d")

    print(f"Running API assertion tests against: {base_url}")

    # 2. Test Root endpoint (Today's hours)
    print("-> Checking Root /")
    status, data = fetch_api(base_url, "/")
    assert status == 200, f"Expected 200, got {status}"
    verify_success_payload(data)

    # 3. Test Valid ISO Date path (Today)
    print(f"-> Checking valid date /{today_str}")
    status, data = fetch_api(base_url, f"/{today_str}")
    assert status == 200, f"Expected 200, got {status}"
    verify_success_payload(data)

    # 4. Test Invalid date string format
    print("-> Checking bad format /not-a-date")
    status, _ = fetch_api(base_url, "/not-a-date")
    assert status == 400, f"Expected 400, got {status}"

    print("All assertions passed successfully!")


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    target_url = target_url.removesuffix("/")

    test_api_routes(target_url)
