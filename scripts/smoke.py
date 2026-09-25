"""Check a deployed container's main endpoints."""
import sys
from urllib.request import urlopen

base = sys.argv[1]
for endpoint, expected in (("/health", b'"status": "ok"'), ("/metrics", b"app_requests_total")):
    with urlopen(base + endpoint, timeout=5) as response:
        assert response.status == 200 and expected in response.read()
print("Deployment smoke checks passed")
