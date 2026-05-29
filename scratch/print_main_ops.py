import json
import os

def get_player_summary(username):
    p = f"data/{username}_stats_processed.json"
    if not os.path.exists(p):
        print(f"{username} has no processed stats")
        return
        
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    y11 = data.get("y11s1", {})
    summary = y11.get("summary", {})
    ops = y11.get("operators", [])
    
    top_op = "N/A"
    if ops:
        sorted_ops = sorted(ops, key=lambda x: x.get("rounds_played", 0), reverse=True)
        main_op = sorted_ops[0]
        top_op = f"{main_op.get('name')} ({main_op.get('rounds_played')}r · {main_op.get('kd_ratio'):.2f} K/D)"
        
    print(f"[{username}]")
    print("  Ranked Rating:", summary.get("ranked_rating"))
    print("  Overall K/D:  ", summary.get("kd"))
    print("  Win Rate:     ", summary.get("win_rate"))
    print("  Main Operator:", top_op)
    print("  Total Ops:    ", len(ops))
    print()

def main():
    for u in ["Amlenk", "WamaiDoingThis", "Covetous_Demon"]:
        get_player_summary(u)

if __name__ == '__main__':
    main()
