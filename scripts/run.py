# run_pipeline.py

import subprocess
import sys
import time
import psutil
import GPUtil
import json

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
    },
    {
        "name": "LLM Group Summarisation",
        "script": "scripts/llm_summary.py"
    },
    {
        "name": "Executive-Level Takeaways",
        "script": "scripts/llm_summary_overall.py"
    }
]

def log_resource_usage(step_name, duration_sec):
    try:
        ram = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.5)
        gpus = GPUtil.getGPUs()
        gpu_mem = sum(g.memoryUsed for g in gpus) if gpus else 0

        metrics = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "step": step_name,
            "duration_sec": round(duration_sec, 2),
            "ram_used_mb": round(ram.used / (1024 * 1024), 2),
            "cpu_percent": round(cpu, 2),
            "gpu_memory_mb": round(gpu_mem, 2)
        }

        with open("data/step_metrics.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(metrics) + "\n")
    except Exception as e:
        print(f"[!] Failed to record metrics for {step_name}: {e}")

def run_step(step, auto_run=False):
    if auto_run:
        print(f"\n[*] Running step: {step['name']}")
        try:
            start = time.perf_counter()
            subprocess.run([sys.executable, step["script"]], check=True)
            end = time.perf_counter()
            log_resource_usage(step["name"], end - start)
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
                start = time.perf_counter()
                subprocess.run([sys.executable, step["script"]], check=True)
                end = time.perf_counter()
                log_resource_usage(step["name"], end - start)
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
