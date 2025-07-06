import json
from collections import defaultdict
import os

ALERTS_FILE = "data/normalized_alerts.jsonl"
SUMMARIES_FILE = "data/alert_summaries.jsonl"
OUTPUT_FILE = "data/grouped_alerts.jsonl"

def load_alerts():
    with open(ALERTS_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f]

def load_summaries():
    with open(SUMMARIES_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f]

def group_alerts(alerts, summaries):
    grouped = defaultdict(lambda: {
        "alerts": [],
        "summaries": [],
        "host": "",
        "user": "",
        "tactic": ""
    })

    for alert, summary in zip(alerts, summaries):
        host = str(alert.get("host", "")).lower().strip() or "unknown_host"
        user = str(alert.get("user", "")).lower().strip() or "unknown_user"
        tactic = str(alert.get("tactic", "")).lower().strip() or "unknown_tactic"

        group_id = f"host-{host}_user-{user}_tactic-{tactic}"

        grouped[group_id]["alerts"].append(alert)
        grouped[group_id]["summaries"].append(summary["summary"])
        grouped[group_id]["host"] = host
        grouped[group_id]["user"] = user
        grouped[group_id]["tactic"] = tactic

    return grouped

def main():
    if not os.path.exists(ALERTS_FILE) or not os.path.exists(SUMMARIES_FILE):
        print("[!] Required input files not found.")
        return

    alerts = load_alerts()
    summaries = load_summaries()

    if len(alerts) != len(summaries):
        print(f"[!] Mismatched alert/summary count: {len(alerts)} alerts, {len(summaries)} summaries")
        return

    grouped = group_alerts(alerts, summaries)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for group_id, group_data in grouped.items():
            f.write(json.dumps({
                "group_id": group_id,
                "host": group_data["host"],
                "user": group_data["user"],
                "tactic": group_data["tactic"],
                "alerts": group_data["alerts"],
                "summaries": group_data["summaries"],
                "alert_count": len(group_data["alerts"])
            }) + "\n")

    print(f"[+] Grouped {len(grouped)} alert sets → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
