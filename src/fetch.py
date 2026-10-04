import json
import time
from pathlib import Path

import requests

RAW_DIR = Path("data/raw")   # where the JSON files get saved
DELAY_SECONDS = 2            # pause between requests, to be polite to the server
MAX_ATTEMPTS = 3             # how many times to try before giving up

# Each item is: (file name to save as, URL to download)
# Replace these with real Judobase URLs once you've found them.
DOWNLOADS = [
    ("test_one", "https://httpbin.org/json"),
    ("test_two", "https://httpbin.org/get"),
]


def fetch_json(url):
    """Download a URL and return the parsed JSON. Tries a few times if it fails."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "judo-portfolio-project (personal, non-commercial)"},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            print(f"  Attempt {attempt} failed: {error}")
            if attempt == MAX_ATTEMPTS:
                raise
            time.sleep(DELAY_SECONDS * attempt)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for name, url in DOWNLOADS:
        path = RAW_DIR / f"{name}.json"

        if path.exists():
            print(f"Skipping {name} (already downloaded)")
            continue

        print(f"Fetching {name}...")
        data = fetch_json(url)
        path.write_text(json.dumps(data, indent=2))
        print(f"  Saved {path}")

        time.sleep(DELAY_SECONDS)


if __name__ == "__main__":
    main()