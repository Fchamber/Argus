#!/usr/bin/env python3
"""Summarize grouped FAISS matches with OpenLLaMA.

- Keeps original paths.
- Adds robust error handling around the Ollama CLI so you can actually see why a run fails (e.g. model not pulled, daemon not running, bad tag).
- Lets you override the model on the command line:  `python scripts/llm_summary.py llama3:8b`.
"""

import json
import subprocess
import os
import sys
from typing import Any, Dict, List

INPUT_FILE = "data/nested_grouped_matches.json"
OUTPUT_FILE = "data/group_summaries.jsonl"
DEFAULT_MODEL = "llama3:8b"  # override with argv[1]


def format_prompt(tactic: str, technique: str, host_user: str, entries: List[Dict[str, Any]]) -> str:
    """Build an LLM‑ready executive‑level prompt from alert entries."""
    sample_descriptions = [e["alert"].get("description", "") for e in entries[:10]]
    sample_text = "\n".join(f"- {desc}" for desc in sample_descriptions)
    return (
        "Summarize the following security alert group in executive terms.\n\n"
        f"MITRE tactic: {tactic}\n"
        f"Technique: {technique}\n"
        f"Host/User group: {host_user}\n\n"
        "Example alert details:\n"
        f"{sample_text}\n\n"
        "Explain what this activity means, the behaviors observed, and what business impact or risk it may imply."
    )


def run_ollama(model: str, prompt: str) -> str:
    """Run an Ollama model locally and return the generated text. Prints helpful diagnostics if the command fails."""
    cmd = ["ollama", "run", model]
    try:
        completed = subprocess.run(
            cmd,
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return completed.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode(errors="ignore").strip()
        print(f"[!] Ollama failed (exit {e.returncode}) while running '{' '.join(cmd)}'", file=sys.stderr)
        if err:
            print("[ollama stderr]", file=sys.stderr)
            print(err, file=sys.stderr)
        print("\nSuggestions:\n"
              "  • Is the Ollama daemon running?  Try `ollama serve` in another terminal.\n"
              "  • Have you pulled the model?   Try `ollama pull " + model + "`.\n"
              "  • Is the tag correct?          Run `ollama list` to see local models.", file=sys.stderr)
        raise


def main() -> None:
    model = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(INPUT_FILE)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        nested: Dict[str, Any] = json.load(f)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        group_count = 0

        # Structure: tactic → technique → host_user → [group, group, ...]
        for tactic, techniques in nested.items():
            for technique, host_users in techniques.items():
                for host_user, groups in host_users.items():
                    for group in groups:  # "groups" is a *list* of grouped-match dicts
                        entries = group.get("entries", [])
                        alert_count = group.get("alert_count", len(entries))

                        prompt = format_prompt(tactic, technique, host_user, entries)
                        print(f"[*] Summarizing {tactic} -> {technique} -> {host_user} ({alert_count} alerts)")
                        summary = run_ollama(model, prompt)

                        out_f.write(
                            json.dumps(
                                {
                                    "tactic": tactic,
                                    "technique": technique,
                                    "host_user": host_user,
                                    "alert_count": alert_count,
                                    "summary": summary,
                                }
                            )
                            + "\n"
                        )

                        group_count += 1
                        print(f"[✓] Completed summary {group_count}")

    print(f"\n[+] Summarized {group_count} groups -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
