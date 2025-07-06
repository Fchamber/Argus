# scripts/normalize_alerts.py

import json

INPUT_FILE = "data/xdr_gui_alerts.json"
OUTPUT_FILE = "data/normalized_alerts.jsonl"

def normalize(alert):
    norm = {
        "source": alert.get("source", "Unknown"),
        "alert_id": alert.get("alert_id") or alert.get("id") or alert.get("uuid") or "",
        "title": alert.get("title") or alert.get("alert_name") or alert.get("Name") or alert.get("threatName") or alert.get("event_type") or "Unknown Alert",
        "tactic": alert.get("tactic") or alert.get("Tactic") or alert.get("attack_tactic") or alert.get("mitreTactic") or "",
        "technique": alert.get("technique") or alert.get("Technique") or alert.get("attack_technique") or alert.get("mitreTechnique") or "",
        "technique_id": alert.get("technique_id") or alert.get("attack_id") or alert.get("techniqueId") or alert.get("mitreID") or "",
        "process": alert.get("process") or alert.get("application") or alert.get("processName") or alert.get("Process") or "",
        "host": alert.get("host") or alert.get("host_name") or alert.get("HostName") or alert.get("agentComputerName") or alert.get("asset_id") or alert.get("resource") or alert.get("src_device") or "",
        "user": alert.get("user") or alert.get("user_name") or alert.get("User") or alert.get("username") or alert.get("principal") or alert.get("userName") or "",
        "timestamp": alert.get("timestamp") or alert.get("log_time") or alert.get("time") or alert.get("event_time") or alert.get("Timestamp") or alert.get("time_detected") or "",
    }

    norm["description"] = f"{norm['title']} involving {norm['process']} on {norm['host']} by {norm['user']}"
    return norm

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        alerts = data.get("alerts", [])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for alert in alerts:
            norm = normalize(alert)
            out_f.write(json.dumps(norm) + "\n")

    print(f"Normalized {len(alerts)} alerts → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
