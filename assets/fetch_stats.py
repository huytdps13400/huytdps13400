#!/usr/bin/env python3
"""Fetches live npm downloads, versions and GitHub stars into assets/stats.json.

Runs daily in .github/workflows/activity.yml; build.py draws the numbers into
the library cards. If a request fails, the previous value is kept.
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

OWNER = "huytdps13400"
PACKAGES = {  # key used by build.py -> (npm package, GitHub repo)
    "ssl": ("react-native-ssl-manager", "react-native-ssl-manager"),
    "iconify": ("@huymobile/react-native-iconify", "react-native-iconify"),
    "sms": ("@huymobile/react-native-sms-retriever-nitro-module", "react-native-sms-retriever-nitro-module"),
    "ota": ("supabase-expo-ota-updates", "supabase-expo-ota-upates"),
    "country": ("@huymobile/react-native-country-codes-picker", "react-native-country-codes-picker"),
}
OUT = Path(__file__).parent / "stats.json"


def get(url, token=None):
    headers = {"User-Agent": f"{OWNER}-profile-stats", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return json.load(r)


def downloads(pkg, since):
    """All-time downloads; the npm API caps ranges at 18 months, so sum per year."""
    total, start, today = 0, since, date.today()
    while start <= today:
        end = min(date(start.year, 12, 31), today)
        total += get(f"https://api.npmjs.org/downloads/point/{start}:{end}/{pkg}").get("downloads", 0)
        start = date(start.year + 1, 1, 1)
    return total


def main():
    stats = json.loads(OUT.read_text()) if OUT.exists() else {}
    token = os.environ.get("GH_TOKEN")
    for key, (pkg, repo) in PACKAGES.items():
        entry = stats.get(key, {})
        try:
            meta = get(f"https://registry.npmjs.org/{urllib.parse.quote(pkg, safe='@')}")
            entry["version"] = meta["dist-tags"]["latest"]
            entry["downloads"] = downloads(pkg, date.fromisoformat(meta["time"]["created"][:10]))
        except Exception as e:  # keep last known numbers
            print(f"! npm {pkg}: {e}")
        try:
            entry["stars"] = get(f"https://api.github.com/repos/{OWNER}/{repo}", token)["stargazers_count"]
        except Exception as e:
            print(f"! github {repo}: {e}")
        stats[key] = entry
        print(key, entry)
    OUT.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
