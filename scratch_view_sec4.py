def main():
    with open("report.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if "SECTION 4: MAP DEEP DIVE" in line or "sec4" in line:
            print(f"\n--- Line {i+1} ---")
            start = max(0, i - 15)
            end = min(len(lines), i + 35)
            for j in range(start, end):
                print(f"{j+1}: {lines[j]}", end="")

if __name__ == '__main__':
    main()
