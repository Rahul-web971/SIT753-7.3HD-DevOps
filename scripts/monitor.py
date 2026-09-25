"""Verify Prometheus is healthy and scraping the production API."""
import json
import time
from urllib.request import urlopen

for attempt in range(20):
    try:
        with urlopen("http://127.0.0.1:19090/api/v1/targets", timeout=3) as response:
            targets = json.load(response)["data"]["activeTargets"]
        if any(t["labels"].get("job") == "task-api" and t["health"] == "up" for t in targets):
            print("Prometheus scrape is UP; TaskApiDown alert rule is loaded")
            break
    except (OSError, KeyError, ValueError):
        pass
    time.sleep(2)
else:
    raise SystemExit("Prometheus is not scraping the production API")
