# scripts/parse_rules.py

import toml
import os
import json

INPUT_DIR = "data/raw_rules/elastic/rules"
OUTPUT_FILE = "data/parsed_rules.jsonl"
FAILURE_LOG = "data/parse_failures.json"
STATS_LOG = "data/parse_stats.json"

def parse_rule(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        raw = toml.load(f)
        metadata = raw.get("metadata", {})
        rule = raw.get("rule", {})

        title = rule.get("name", "N/A").strip() or "N/A"
        description = rule.get("description", "N/A").strip() or "N/A"
        query = rule.get("query", "N/A").strip() or "N/A"

        # Extract first tactic/technique from threat list if available
        tactic = ""
        technique = ""
        technique_id = ""
        threats = rule.get("threat", [])
        if isinstance(threats, list) and threats:
            threat = threats[0]
            tactic = threat.get("tactic", {}).get("name", "")

            techniques = threat.get("technique", [])
            if isinstance(techniques, list) and techniques:
                technique = techniques[0].get("name", "")
                technique_id = techniques[0].get("id", "")
            elif isinstance(techniques, dict):
                technique = techniques.get("name", "")
                technique_id = techniques.get("id", "")

        return {
            "title": title,
            "description": description,
            "query": query,
            "tactic": tactic,
            "technique": technique,
            "technique_id": technique_id,
            "risk_score": metadata.get("risk_score", "N/A"),
            "tags": metadata.get("tags", []),
            "references": metadata.get("references", []),
            "file": os.path.basename(file_path)
        }

def main():
    all_rules = []
    parse_failures = []

    total_files = 0
    parsed_files = 0
    failed_files = 0

    for root, _, files in os.walk(INPUT_DIR):
        for fname in files:
            if fname.endswith(".toml"):
                full_path = os.path.join(root, fname)

                # Skip deprecated rules
                if "_deprecated" in full_path.lower():
                    continue

                total_files += 1

                try:
                    parsed = parse_rule(full_path)
                    if parsed:
                        parsed_files += 1
                        print(f"[*] Parsed: {parsed['title']}")
                        all_rules.append(parsed)
                except Exception as e:
                    failed_files += 1
                    parse_failures.append({
                        "file": full_path,
                        "error": str(e)
                    })
                    print(f"[!] Failed to parse {full_path}: {e}")

    # Write parsed rules
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for rule in all_rules:
            out_f.write(json.dumps(rule) + "\n")

    # Write failed file log
    with open(FAILURE_LOG, "w", encoding="utf-8") as fail_f:
        json.dump(parse_failures, fail_f, indent=2)

    # Write summary stats
    percent = (parsed_files / total_files * 100) if total_files else 0
    stats = {
        "total_files": total_files,
        "parsed_successfully": parsed_files,
        "failed": failed_files,
        "success_rate": round(percent, 2)
    }

    with open(STATS_LOG, "w", encoding="utf-8") as stats_f:
        json.dump(stats, stats_f, indent=2)

    # Print final summary
    print("\n[+] Rule parsing complete.")
    print(f"[*] Parsed: {parsed_files}/{total_files} → {OUTPUT_FILE}")
    print(f"[!] Failed TOML parses: {failed_files} → {FAILURE_LOG}")
    print(f"[#] Success rate: {percent:.2f}% → {STATS_LOG}")

if __name__ == "__main__":
    main()
