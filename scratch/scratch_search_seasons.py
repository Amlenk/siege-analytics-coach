import os
import json

for f_name in os.listdir("data/raw"):
    if f_name.endswith(".json"):
        path = os.path.join("data", "raw", f_name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if "Silent Hunt" in content or "season 41" in content or "season\": 41" in content:
                print(f"Found references in: {f_name}")
        except Exception as e:
            pass
