# run_pipeline.py

import subprocess
import sys

steps = [
    {
        "name": "Parse Rules",
        "script": "scripts/parse_rules.py"
    },
    {
        "name": "Embed Rules into FAISS Index",
        "script": "scripts/embed_chunks.py"
    },
    {
        "name": "Normalize Alerts",
        "script": "scripts/normalize_alerts.py"
    },
    {
        "name": "Query FAISS with First Alert",
        "script": "scripts/query_faiss.py"
    },
    {
        "name": "Group FAISS Matches",
        "script": "scripts/group_faiss_matches.py"
    },
    {
        "name": "Nest Grouped Matches",
        "script": "scripts/nest_grouped_matches.py"
    }
]

def run_step(step, auto_run=False):
    if auto_run:
        print(f"\n[*] Running step: {step['name']}")
        try:
            subprocess.run([sys.executable, step["script"]], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] Error in step: {step['name']}")
            print(e)
        return True, True

    print(f"\n[*] Step: {step['name']}")
    while True:
        choice = input("→ Run this step? (Y = yes, N = skip, C = cancel, A = run all): ").strip().upper()
        if choice == "Y":
            print(f"[>] Running: {step['script']}")
            try:
                subprocess.run([sys.executable, step["script"]], check=True)
            except subprocess.CalledProcessError as e:
                print(f"[!] Error in step: {step['name']}")
                print(e)
            return True, False
        elif choice == "N":
            print("[~] Skipping this step.")
            return True, False
        elif choice == "C":
            print("[x] Pipeline cancelled.")
            return False, False
        elif choice == "A":
            print("[*] Running all remaining steps automatically.")
            return run_step(step, auto_run=True)
        else:
            print("[!] Invalid choice. Enter Y, N, C, or A.")

def main():
    print("=== RAG Pipeline Runner ===")
    auto_run = False
    for step in steps:
        continue_run, auto_run = run_step(step, auto_run=auto_run)
        if not continue_run:
            break
    print("\n[+] Pipeline complete (or cancelled).")

if __name__ == "__main__":
    main()
