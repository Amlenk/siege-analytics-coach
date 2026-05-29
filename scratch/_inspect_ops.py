import json
for user in ["Amlenk", "WamaiDoingThis", "Covetous_Demon"]:
    try:
        data = json.load(open(f'data/{user}_stats_processed.json', 'r'))
        scope = "y11s1" if "y11s1" in data else "lifetime"
        ops = sorted(data[scope]["operators"], key=lambda x: x.get('rounds_played', 0), reverse=True)
        print(f"=== {user} top ops ===")
        for o in ops[:8]:
            print(f"  {o['name']}: {o['rounds_played']} rounds, {o['win_rate']} WR, {o['kd_ratio']:.2f} KD")
    except Exception as e:
        print(f"Error for {user}: {e}")
