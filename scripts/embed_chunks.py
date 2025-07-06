# scripts/embed_chunks.py

import json
import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer

RULES_FILE = "data/parsed_rules.jsonl"
FAISS_INDEX_FILE = "data/faiss_index.bin"
METADATA_FILE = "data/faiss_metadata.pkl"
EMBED_MODEL = "all-MiniLM-L6-v2"  # fast, decent quality

def load_rules():
    rules = []
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            rules.append(json.loads(line.strip()))
    return rules

def rule_to_text(rule):
    return f"{rule['title']}\n{rule['technique_id']} {rule['technique']} ({rule['tactic']})\n{rule['description']}\n{rule['query']}"

def main():
    print("Loading rules...")
    rules = load_rules()
    texts = [rule_to_text(rule) for rule in rules]

    print(f"Embedding {len(texts)} rules...")
    model = SentenceTransformer(EMBED_MODEL)
    embeddings = model.encode(texts, convert_to_numpy=True)

    print("Creating FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    print(f"Indexed {index.ntotal} vectors")

    print("Saving index and metadata...")
    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(rules, f)

    print("Done - Vector index saved.")

if __name__ == "__main__":
    main()
