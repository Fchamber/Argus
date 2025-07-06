import json
import os

INPUT_FILE = "data/grouped_alerts.jsonl"
OUTPUT_FILE = "data/grouped_alerts.json"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[!] Input file not found: {INPUT_FILE}")
        return

    groups = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            groups.append(json.loads(line.strip()))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=2)

    print(f"[+] Converted to JSON array → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
