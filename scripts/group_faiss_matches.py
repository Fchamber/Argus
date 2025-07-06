import json
import os
from collections import defaultdict

INPUT_FILE = "data/alert_matches.jsonl"
OUTPUT_FILE = "data/grouped_matches.jsonl"

def load_alert_matches(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f]

def group_matches(matches):
    grouped = defaultdict(lambda: {
        "alerts": [],
        "host": "",
        "user": "",
        "tactic": "",
        "match_count": 0
    })

    for match in matches:
        alert = match.get("alert", {})
        rule = match.get("matched_rule", {})

        host = str(alert.get("host", "")).lower().strip() or "unknown_host"
        user = str(alert.get("user", "")).lower().strip() or "unknown_user"
        tactic = str(alert.get("tactic", "")).lower().strip() or "unknown_tactic"

        group_id = f"host-{host}_user-{user}_tactic-{tactic}"

        grouped[group_id]["alerts"].append({
            "alert": alert,
            "matched_rule": rule,
            "score": match.get("score", 0.0)
        })
        grouped[group_id]["host"] = host
        grouped[group_id]["user"] = user
        grouped[group_id]["tactic"] = tactic
        grouped[group_id]["match_count"] += 1

    return grouped

def save_grouped_matches(grouped, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for group_id, group in grouped.items():
            group_data = {
                "group_id": group_id,
                "host": group["host"],
                "user": group["user"],
                "tactic": group["tactic"],
                "alert_count": group["match_count"],
                "entries": group["alerts"]
            }
            f.write(json.dumps(group_data) + "\n")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[!] Input file not found: {INPUT_FILE}")
        return

    matches = load_alert_matches(INPUT_FILE)
    grouped = group_matches(matches)
    save_grouped_matches(grouped, OUTPUT_FILE)

    print(f"[+] Grouped {len(grouped)} sets of FAISS alert matches → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
