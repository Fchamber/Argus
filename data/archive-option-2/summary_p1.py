# scripts/generate_summary.py

import json
import pickle
import faiss
import requests
from sentence_transformers import SentenceTransformer

ALERTS_FILE = "data/normalized_alerts.jsonl"
FAISS_INDEX_FILE = "data/faiss_index.bin"
METADATA_FILE = "data/faiss_metadata.pkl"
OUTPUT_FILE = "data/alert_summaries.jsonl"
MODEL_NAME = "llama3:8b"

def load_alerts():
    with open(ALERTS_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f]

def load_faiss():
    index = faiss.read_index(FAISS_INDEX_FILE)
    with open(METADATA_FILE, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def format_prompt(alert, matches):
    context_lines = []
    for i, rule in enumerate(matches):
        context_lines.append(f"[{i+1}] {rule.get('title', 'Untitled')}: {rule.get('description', '')}")

    context = "\n".join(context_lines)
    alert_description = f"Alert: {alert['title']} - {alert['description']}"

    prompt = (
        f"You are a security analyst. Summarize the alert and its related rules into a short, high-impact explanation "
        f"suitable for a C-suite audience.\n\n"
        f"{alert_description}\n\n"
        f"Top Related Rules:\n{context}\n\n"
        f"Summary:"
    )
    return prompt

def query_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )
    return response.json().get("response", "").strip()

def main():
    alerts = load_alerts()
    index, metadata = load_faiss()
    model = SentenceTransformer("all-MiniLM-L6-v2")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for alert in alerts:
            text = " ".join(str(alert.get(f, "")) for f in ["title", "description", "tactic", "technique", "process"])
            embedding = model.encode([text])
            distances, indices = index.search(embedding, k=5)
            matches = [metadata[i] for i in indices[0]]

            prompt = format_prompt(alert, matches)
            summary = query_ollama(prompt)

            output = {
                "alert": alert,
                "summary": summary
            }

            out_f.write(json.dumps(output) + "\n")
            print(f"[+] Summarized: {alert['title']}")

    print(f"\n[#] Completed summaries → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
