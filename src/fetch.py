import asyncio
import json
from pathlib import Path

from judobase import JudoBase

RAW_DIR = Path("data/raw")
DELAY_SECONDS = 1      # pause between athlete requests
MAX_ATHLETES = 30      # sample size per competition for the feasibility check

# 994 = 2010 World Masters, 2653 = Paris 2024 Olympics
# (assumes ijf.org competition IDs match the API's; verify in the output)
COMPETITION_IDS = [994, 2653]


def save_json(data, path):
    """Write data to a JSON file, creating folders if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


async def fetch_competition(api, competition_id):
    comp_dir = RAW_DIR / f"competition_{competition_id}"

    # 1. Competition info
    info_path = comp_dir / "info.json"
    if info_path.exists():
        print(f"Skipping info for {competition_id} (already downloaded)")
    else:
        print(f"Fetching info for {competition_id}...")
        competition = await api.competition_by_id(competition_id)
        save_json(competition.model_dump(mode="json"), info_path)

    # 2. Contests (matches), including events
    contests_path = comp_dir / "contests.json"
    if contests_path.exists():
        print(f"Skipping contests for {competition_id} (already downloaded)")
    else:
        print(f"Fetching contests for {competition_id}...")
        contests = await api.contests_by_competition_id(
            competition_id, include_events=True
        )
        save_json([c.model_dump(mode="json") for c in contests], contests_path)

    # Always work from the saved file, whether we just wrote it or not
    contests = json.loads(contests_path.read_text())
    print(f"  {len(contests)} contests")

    # 3. A sample of athlete profiles (for height, birth date)
    athlete_ids = set()
    for contest in contests:
        athlete_ids.add(contest["id_person_blue"])
        athlete_ids.add(contest["id_person_white"])

    for athlete_id in sorted(athlete_ids)[:MAX_ATHLETES]:
        athlete_path = comp_dir / "athletes" / f"{athlete_id}.json"
        if athlete_path.exists():
            continue

        try:
            judoka = await api.judoka_by_id(athlete_id)
        except Exception as error:
            print(f"  Could not fetch athlete {athlete_id}: {error}")
            continue

        save_json(judoka.model_dump(mode="json"), athlete_path)
        await asyncio.sleep(DELAY_SECONDS)


async def main():
    async with JudoBase() as api:
        for competition_id in COMPETITION_IDS:
            await fetch_competition(api, competition_id)


if __name__ == "__main__":
    asyncio.run(main())