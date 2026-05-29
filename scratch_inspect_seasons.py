import json

def main():
    with open('scratch_seasonsStats.json', 'r') as f:
        data = json.load(f)
        
    segments = data.get("data", {}).get("segments", [])
    
    for s in segments:
        attr = s.get("attributes", {})
        if attr.get("gamemode") == "pvp_ranked" and attr.get("season") is None:
            print("--- None Season Ranked Segment Detail ---")
            print("Attributes:", attr)
            print("Metadata:", s.get("metadata"))
            print("Stats sample:")
            for k, v in s.get("stats", {}).items():
                print(f"  {k}: {v}")

if __name__ == '__main__':
    main()
