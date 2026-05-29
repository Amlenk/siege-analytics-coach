import json

def main():
    try:
        with open("data/raw/r6data_ops_raw.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        ops = []
        if isinstance(data, list):
            ops = data
        elif isinstance(data, dict):
            ops = data.get("operators", [])
            
        total_kills = 0
        total_deaths = 0
        total_wins = 0
        total_losses = 0
        total_rounds = 0
        
        for op in ops:
            total_kills += int(op.get("kills", 0))
            total_deaths += int(op.get("deaths", 0))
            total_wins += int(op.get("wins", 0))
            total_losses += int(op.get("losses", 0))
            total_rounds += int(op.get("roundsPlayed", 0))
            
        print("=== AGGREGATE STATS ===")
        print("Total Kills:", total_kills)
        print("Total Deaths:", total_deaths)
        print("Total Wins:", total_wins)
        print("Total Losses:", total_losses)
        print("Total Rounds:", total_rounds)
        
        kd = total_kills / max(total_deaths, 1)
        wr = (total_wins / max(total_wins + total_losses, 1)) * 100
        print(f"Calculated K/D: {kd:.2f}")
        print(f"Calculated Win Rate: {wr:.2f}%")
        
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
