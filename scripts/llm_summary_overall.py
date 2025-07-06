#!/usr/bin/env python3
"""
org_takeaways_retry_forever.py
──────────────────────────────
• Step 1 – ask the LLM for a JSON array of 5 titles; retry until it parses.
• Step 2 – for each title, ask for a JSON object with keys:
            {"what": "...", "impact": "...", "mitigation": "..."}
           …again retrying until JSON parses.

Outputs
-------
data/top5_takeaways.txt   – plain text (diff-friendly)
data/top5_takeaways.html  – polished HTML for execs
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from html import escape
from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

GROUP_SUMMARIES = Path("data/group_summaries.jsonl")
TXT_OUT         = Path("data/top5_takeaways.txt")
HTML_OUT        = Path("data/top5_takeaways.html")
MODEL_TAG       = sys.argv[1] if len(sys.argv) > 1 else "openllama:3.1-8b"
RETRY_DELAY_S   = 2          # seconds to wait between retries

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ask_llm(prompt: str) -> str:
    """Run Ollama and return stdout (raises RuntimeError on failure)."""
    proc = subprocess.run(
        ["ollama", "run", MODEL_TAG],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode(errors="ignore"))
    return proc.stdout.decode().strip()


def scan_json(text: str, opener: str, closer: str) -> Any:
    """Return first syntactically-valid JSON substring (raises if none)."""
    start = text.find(opener)
    while start != -1:
        depth = 0
        for idx in range(start, len(text)):
            ch = text[idx]
            if ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    snippet = text[start : idx + 1]
                    try:
                        return json.loads(snippet)
                    except json.JSONDecodeError:
                        break
        start = text.find(opener, start + 1)
    raise ValueError("no valid JSON block found")


def build_context(gs: List[Dict[str, Any]]) -> str:
    """Readable bullet list of alert-group summaries."""
    return "\n".join(
        f"- [{g['alert_count']} alerts] {g['tactic']}/{g['technique']} "
        f"on {g['host_user']}: {g['summary']}"
        for g in sorted(gs, key=lambda g: g.get("alert_count", 0), reverse=True)
    )


def html_report(items: List[Dict[str, str]]) -> str:
    blocks = []
    for i, it in enumerate(items, 1):
        blocks.append(
            f"<section class='takeaway'>\n"
            f"  <h2>{i}. {escape(it['title'])}</h2>\n"
            f"  <ul>\n"
            f"    <li><strong>What this means:</strong> {escape(it['what'])}</li>\n"
            f"    <li><strong>What impact:</strong> {escape(it['impact'])}</li>\n"
            f"    <li><strong>How to mitigate:</strong> {escape(it['mitigation'])}</li>\n"
            f"  </ul>\n"
            f"</section>"
        )
    return f"""<!DOCTYPE html>
<html lang='en'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Top 5 Security Takeaways</title>
<style>
 body{{margin:0;padding:2rem 1rem;font-family:-apple-system,BlinkMacSystemFont,
 'Segoe UI',Helvetica,Arial,sans-serif;line-height:1.6;background:#fff;color:#1a1a1a;}}
 @media(prefers-color-scheme:dark){{body{{background:#121212;color:#e0e0e0;}}}}
 main{{max-width:56rem;margin:auto;}}
 h1{{font-size:1.9rem;color:#0366d6;margin-bottom:1.5rem;}}
 h2{{font-size:1.25rem;margin:1.25rem 0 .6rem;}}
 ul{{padding-left:1.25rem;margin:0 0 1.2rem;}}
 li{{margin-bottom:.5rem;}}
 strong{{color:#555;}}
</style></head><body><main>
<h1>Key Security Takeaways</h1>
{''.join(blocks)}
</main></body></html>"""


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

TITLES_PROMPT = (
    "Return ONLY a JSON array (no markdown, no commentary) of exactly five short, "
    "distinct risk titles based on the context below.\n\nContext:\n{context}"
)

DETAIL_PROMPT = (
    "Return ONLY a JSON object with keys 'what', 'impact', 'mitigation'. "
    "Each value must be 1–2 plain sentences, no other keys, no markdown. "
    'Risk title: "{title}".'
)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not GROUP_SUMMARIES.exists():
        sys.exit("Error: data/group_summaries.jsonl missing – run group-summary step first.")

    groups = [json.loads(l) for l in GROUP_SUMMARIES.read_text().splitlines() if l.strip()]
    context = build_context(groups)

    # Step 1 – titles (retry until JSON array of 5)
    while True:
        try:
            titles_raw = ask_llm(TITLES_PROMPT.format(context=context))
            titles = scan_json(titles_raw, "[", "]")
            if isinstance(titles, list) and len(titles) == 5:
                break
            raise ValueError("array length != 5")
        except Exception as e:
            print(f"[!] Titles JSON parse failed: {e}\n    Retrying in {RETRY_DELAY_S}s…")
            time.sleep(RETRY_DELAY_S)

    # Step 2 – details per title (retry each until valid JSON object)
    results: List[Dict[str, str]] = []
    txt_lines: List[str] = []

    for idx, title in enumerate(titles, 1):
        while True:
            try:
                detail_raw = ask_llm(DETAIL_PROMPT.format(title=title))
                detail = scan_json(detail_raw, "{", "}")
                if all(detail.get(k, "").strip() for k in ("what", "impact", "mitigation")):
                    break
                raise ValueError("missing keys")
            except Exception as e:
                print(f"[!] JSON parse failed for '{title}': {e}\n    Retrying in {RETRY_DELAY_S}s…")
                time.sleep(RETRY_DELAY_S)

        results.append({"title": title, **detail})
        txt_lines.extend([
            f"{idx}. {title}",
            f"- What this means: {detail['what']}",
            f"- What impact: {detail['impact']}",
            f"- How to mitigate: {detail['mitigation']}",
            ""
        ])

    # Save outputs
    TXT_OUT.parent.mkdir(parents=True, exist_ok=True)
    TXT_OUT.write_text("\n".join(txt_lines), encoding="utf-8")
    HTML_OUT.write_text(html_report(results), encoding="utf-8")
    print(f"[+] Results written -> {TXT_OUT} | {HTML_OUT}")


if __name__ == "__main__":
    main()
