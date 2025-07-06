import json
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import os

ALERT_FILE = "data/normalized_alerts.jsonl"
FAISS_INDEX_FILE = "data/faiss_index.bin"
METADATA_FILE = "data/faiss_metadata.pkl"
OUTPUT_FILE = "data/alert_matches.jsonl"
EMBED_MODEL = "all-MiniLM-L6-v2"

def load_alerts():
    with open(ALERT_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f]

def load_index_and_metadata():
    index = faiss.read_index(FAISS_INDEX_FILE)
    with open(METADATA_FILE, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def alert_to_text(alert):
    fields = [
        alert.get("title", ""),
        alert.get("description", ""),
        alert.get("tactic", ""),
        alert.get("technique", ""),
        alert.get("process", ""),
        alert.get("host", ""),
        alert.get("user", "")
    ]
    return " ".join(str(f).strip() for f in fields if f)

def main():
    if not os.path.exists(ALERT_FILE):
        print("[!] Normalized alerts not found.")
        return

    model = SentenceTransformer(EMBED_MODEL)
    index, metadata = load_index_and_metadata()
    alerts = load_alerts()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for alert in alerts:
            alert_text = alert_to_text(alert)
            query_vector = model.encode([alert_text])
            distances, indices = index.search(query_vector, k=5)

            match_set = []
            for i, idx in enumerate(indices[0]):
                rule = metadata[idx]
                match_set.append({
                    "title": rule.get("title", ""),
                    "tactic": rule.get("tactic", ""),
                    "technique": rule.get("technique", ""),
                    "technique_id": rule.get("technique_id", ""),
                    "query": rule.get("query", ""),
                    "description": rule.get("description", ""),
                    "risk_score": rule.get("risk_score", ""),
                    "tags": rule.get("tags", []),
                    "references": rule.get("references", []),
                    "score": float(distances[0][i])
                })

            out_f.write(json.dumps({
                "alert": alert,
                "matches": match_set
            }) + "\n")

    print(f"[+] Matched {len(alerts)} alerts with FAISS rules → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
