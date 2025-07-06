# Argus
Retrevial-Augmented Generation LLM tool for CS Reporting

Argus: LLM-Driven Cybersecurity Executive Reporting
====================================================

Argus is a proof-of-concept tool for generating executive-level cybersecurity summaries using synthetic XDR alerts and open-source detection rules. It implements a Retrieval-Augmented Generation (RAG) pipeline using a locally hosted language model, designed for use in privacy-sensitive environments such as Managed Service Providers (MSPs).

This project was developed as part of an academic research investigation into local, explainable AI summarisation pipelines for multi-platform cybersecurity telemetry.

----------------------------------------------------
Purpose
----------------------------------------------------

The Argus pipeline addresses a common operational challenge: transforming noisy, low-level security alerts into concise, high-impact executive summaries. It enables:

- Schema-agnostic alert ingestion from multiple XDR vendors
- Semantic retrieval of relevant detection logic using FAISS
- Grounded summarisation using OpenLLaMA (quantised for GPU efficiency)
- Executive reporting outputs including key findings and mitigation advice

----------------------------------------------------
Features
----------------------------------------------------

- Normalisation of synthetic alerts from Elastic, SentinelOne, Defender, CrowdStrike, Carbon Black, and others
- Retrieval of matched Elastic Security rules via vector embedding (sentence-transformers + FAISS)
- Two-pass summarisation: individual group summaries followed by high-level takeaways
- Local-only processing for full data privacy (no API or cloud inference required)
- MITRE ATT&CK alignment and inline provenance in all outputs
- HTML executive report generation with structured findings

----------------------------------------------------
Repository Structure
----------------------------------------------------

argus-rag-summary/
├── data/                    # Normalised alerts, group summaries, FAISS index (excluded from Git)
├── scripts/                 # All modular Python components
│   ├── parse_rules.py
│   ├── embed_chunks.py
│   ├── normalize_alerts.py
│   ├── query_faiss.py
│   ├── group_faiss_matches.py
│   ├── nest_grouped_matches.py
│   ├── llm_summary.py
│   └── llm_summary_overall.py
├── run.py                   # Interactive pipeline runner
├── requirements.txt         # Python package dependencies
├── README.txt               # This file
├── LICENSE                  # MIT license
└── .gitignore               # Git exclusions for data and artefacts

----------------------------------------------------
Getting Started
----------------------------------------------------

Prerequisites:

- Python 3.10 or newer
- pip
- A local Ollama-compatible LLM installed (e.g., openllama:3.1-8b)
- Basic GPU (6 GB VRAM or more recommended for quantised model inference)

Installation:

1. Clone the repository:

   git clone https://github.com/YOUR_USERNAME/argus-rag-summary.git
   cd argus-rag-summary

2. Install dependencies:

   pip install -r requirements.txt

3. Pull the LLM model via Ollama if needed:

   ollama pull openllama:3.1-8b

----------------------------------------------------
Running the Pipeline
----------------------------------------------------

Launch the interactive pipeline:

   python run.py

You will be prompted to run each of the following stages:

1. Parse Elastic detection rules from TOML
2. Embed them into a FAISS vector index
3. Normalise alerts from a synthetic dataset
4. Run FAISS similarity search per alert
5. Group alerts by host/user/tactic
6. Nest alert groups for summarisation

Then, run:

   python scripts/llm_summary.py
   python scripts/llm_summary_overall.py

Final output will be in:

- data/group_summaries.jsonl       (Individual group summaries)
- data/top5_takeaways.txt          (Five executive-level takeaways)
- data/top5_takeaways.html         (HTML version for executive reporting)

----------------------------------------------------
Outputs
----------------------------------------------------

Each summarised group includes:

- MITRE tactic and technique
- Host and user context
- Number of alerts matched
- A grounded natural language summary with risk implications

Each executive takeaway includes:

- Title
- What this means
- Business impact
- Recommended mitigation

----------------------------------------------------
Licensing
----------------------------------------------------

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).

You may use, share, and adapt this code for research and non-commercial purposes, provided that appropriate credit is given. Commercial use of any kind is prohibited without prior written permission.

Full license text: https://creativecommons.org/licenses/by-nc/4.0/

----------------------------------------------------
Academic Context
----------------------------------------------------

This tool was developed as part of a postgraduate IT project investigating explainable, privacy-preserving summarisation architectures for cross-platform security alerts. It follows a Design Science Research methodology and uses entirely synthetic alert data.

All detections are derived from Elastic Security’s open-source rule corpus. No production data is used or required.

----------------------------------------------------
Limitations and Future Work
----------------------------------------------------

- Designed for batch summarisation, not real-time ingestion
- Tested on synthetic alert corpora, not live telemetry
- Limited to 3.1B parameter models for performance on modest GPUs

Planned enhancements include:

- Support for real-world alert formats
- Human-in-the-loop feedback options
- Continuous ingestion pipelines
- Visual explainability layers

----------------------------------------------------
Disclaimer
----------------------------------------------------

This tool is provided for research and educational purposes. It is not a certified detection engine or commercial security product. Use caution before deploying in production environments.
