import json
import os

def main():
    path = "data/raw/WamaiDoingThis_seasons_history.json"
    if not os.path.exists(path):
        print(f"File {path} does not exist.")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Metadata:", data.get("data", {}).get("metadata"))
    segments = data.get("data", {}).get("segments", [])
    print(f"Total segments: {len(segments)}")

    for idx, s in enumerate(segments):
        attr = s.get("attributes", {})
        metadata = s.get("metadata", {})
        stats = s.get("stats", {})
        if attr.get("gamemode") == "pvp_ranked":
            season_id = attr.get("season")
            short_name = metadata.get("shortName")
            name = metadata.get("name")
            matches = stats.get("matchesPlayed", {}).get("value")
            rp = stats.get("rankPoints", {}).get("value")
            wins = stats.get("matchesWon", {}).get("value")
            losses = stats.get("matchesLost", {}).get("value")
            kills = stats.get("kills", {}).get("value")
            deaths = stats.get("deaths", {}).get("value")
            print(f"Segment {idx}: Season ID={season_id}, Name={name}, Short={short_name}, Matches={matches}, Wins={wins}, Losses={losses}, RP={rp}, Kills={kills}, Deaths={deaths}")

if __name__ == '__main__':
    main()
