"""Check source URL reachability; a fetch is not source-content validation."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime, timezone
import json
import re

ROOT = Path(__file__).resolve().parents[1]
urls = set()
for file in ROOT.rglob("*.md"):
    urls.update(re.findall(r"\]\((https?://[^)]+)\)", file.read_text(encoding="utf-8")))


def check(url):
    try:
        request = Request(url, headers={"User-Agent": "SoftwareEngineeringStudy-LinkAudit/1.0"})
        with urlopen(request, timeout=15) as response:
            response.read(1024)
            return {"url": url, "status": response.status, "resolved": response.url}
    except HTTPError as exc:
        return {"url": url, "status": exc.code, "error": str(exc)}
    except Exception as exc:
        return {"url": url, "status": None, "error": str(exc)}


results = []
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(check, url): url for url in sorted(urls)}
    for i, future in enumerate(as_completed(futures), 1):
        result = future.result()
        results.append(result)
        if result["status"] is None or result["status"] >= 400:
            print(json.dumps(result), flush=True)
        if i % 50 == 0:
            print(f"Checked {i}/{len(urls)} sources", flush=True)
report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
          "results": sorted(results, key=lambda x: x["url"])}
(ROOT / "tools/external-link-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(f"Finished checking {len(urls)} external URLs", flush=True)
