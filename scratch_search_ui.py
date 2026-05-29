import re
import glob

def search_files(pattern):
    print(f"=== SEARCHING FOR '{pattern}' ===")
    for fn in glob.glob("*.py") + glob.glob("*.html") + glob.glob("*.css"):
        try:
            with open(fn, 'r', encoding='utf-8') as f:
                content = f.read()
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                print(f"File {fn}: found {len(matches)} matches")
                for m in matches[:3]:
                    start = max(0, m.start() - 60)
                    end = min(len(content), m.end() + 100)
                    print(f"  ... {content[start:end].strip().replace('\n', ' ')} ...")
        except Exception as e:
            print(f"Error reading {fn}: {e}")

if __name__ == '__main__':
    search_files("deep dive")
    search_files("map-card")
    search_files("maps-grid")
    search_files("box-in-box")
