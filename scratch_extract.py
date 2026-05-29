def main():
    with open("r6data_fetch.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Print the exact target content from line 306 (which is index 305) to the end
    target = "".join(lines[305:])
    
    # Save the target content to a temporary scratch file so we can reference it exactly
    with open("scratch/target_r6data_fetch.txt", "w", encoding="utf-8") as f:
        f.write(target)
    print("Successfully saved target to scratch/target_r6data_fetch.txt")
    print(f"Target length: {len(target)} chars, lines: {len(lines[305:])}")

if __name__ == '__main__':
    main()
