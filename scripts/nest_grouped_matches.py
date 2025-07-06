# scripts/nest_grouped_matches.py

import json
from collections import defaultdict
import os

INPUT_FILE = "data/grouped_matches.jsonl"
OUTPUT_FILE = "data/nested_grouped_matches.jsonl"

def load_grouped_matches():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f]

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[!] Input file not found: {INPUT_FILE}")
        return

    print("[*] Loading grouped match entries...")
    matches = load_grouped_matches()
    print(f"[+] Loaded {len(matches)} grouped entries")

    print("[*] Consolidating entries by tactic, technique, host, user...")
    grouped = defaultdict(list)

    for entry in matches:
        tactic = str(entry.get("tactic", "unknown")).strip()
        technique = str(entry.get("technique", "unknown")).strip()
        host = str(entry.get("host", "unknown")).strip()
        user = str(entry.get("user", "unknown")).strip()
        summary = entry.get("summary", "").strip()

        key = (tactic, technique, host, user)
        if summary:
            grouped[key].append(summary)

    print(f"[+] Generated {len(grouped)} unique groups")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for (tactic, technique, host, user), summaries in grouped.items():
            record = {
                "tactic": tactic,
                "technique": technique,
                "host": host,
                "user": user,
                "summaries": summaries
            }
            f.write(json.dumps(record) + "\n")

    print(f"[✓] Output written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
