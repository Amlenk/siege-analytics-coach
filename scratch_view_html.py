def main():
    import os
    fn = "output/Amlenk_report.html"
    if not os.path.exists(fn):
        print("Amlenk report not found!")
        return
        
    print(f"Reading {fn}...")
    with open(fn, 'r', encoding='utf-8') as f:
        content = f.read()
        
    idx = content.find('id="deepdive"')
    if idx != -1:
        print("Found id='deepdive'!")
        # Print the next 1500 chars to inspect the div nesting
        print(content[idx:idx+1500])
    else:
        print("Could not find id='deepdive'")

if __name__ == '__main__':
    main()
