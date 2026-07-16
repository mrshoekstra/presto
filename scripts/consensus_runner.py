#!/usr/bin/env python3
"""Fable-5 consensus runner — inference-time compute harness.

Buys reasoning quality that prompting alone cannot: samples N candidate
responses in parallel under the Fable-5 contract, scores each with a judge
model against the contract's audit gate, and returns the winner. Optionally
runs a critic pass on the winner and regenerates once if it fails the gate.

This is the contract's simulated consensus loop made real. Cost is roughly
(N + 1) * single-call tokens; +2 calls with --critic.

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python scripts/consensus_runner.py "How should we shard this database?"
    python scripts/consensus_runner.py --n 5 --tier T2 --critic "..."
    echo "question" | python scripts/consensus_runner.py -
"""
import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:
    import anthropic
except ImportError:
    sys.exit("anthropic SDK not installed: pip install anthropic")

CONTRACT = (
    Path(__file__).resolve().parent.parent / "output-styles" / "fable-5.md"
).read_text().split("---", 2)[2].strip()

# Tier -> extended-thinking budget (Claude models). T0 skips thinking.
THINKING_BUDGET = {"T0": 0, "T1": 4000, "T2": 16000}

JUDGE_PROMPT = """You are scoring candidate answers against a behavioral
contract's audit gate. Return ONLY JSON:
{"scores": [{"index": int, "outcome_first": 0-2, "anchored": 0-2,
"committed": 0-2, "density": 0-2, "correctness_risk": 0-2}]}
correctness_risk: 2 = no visible errors, 0 = likely wrong.

QUESTION:
%s

CANDIDATES:
%s"""

CRITIC_PROMPT = """Audit this answer against the checklist. Return ONLY JSON:
{"pass": bool, "failures": ["..."]}.
Checklist: first sentence is the verdict; every factual claim anchored or
labeled unverified; one committed recommendation per decision point; no
filler, hedging stacks, or closing offers; depth matches stakes.

QUESTION:
%s

ANSWER:
%s"""


def strip_thought(text: str) -> str:
    return re.sub(r"<thought_process>.*?</thought_process>\s*", "", text,
                  flags=re.DOTALL).strip()


def extract_json(text: str) -> dict:
    start, end = text.index("{"), text.rindex("}") + 1
    return json.loads(text[start:end])


def sample(client, model: str, question: str, tier: str) -> str:
    budget = THINKING_BUDGET[tier]
    kwargs = {
        "model": model,
        "max_tokens": 4096 + budget,
        "system": [{"type": "text", "text": CONTRACT,
                    "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": question}],
    }
    if budget:
        # Thinking requires temperature 1; the judge replaces the
        # low-temperature stability lever. Diversity comes free.
        kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}
        kwargs["temperature"] = 1
    else:
        # No hidden channel in use: prefill forces the S2 stage, sample
        # warm for diversity across candidates.
        kwargs["temperature"] = 0.7
        kwargs["messages"] = kwargs["messages"] + [
            {"role": "assistant", "content": "<thought_process>\nTIER:"}]
    resp = client.messages.create(**kwargs)
    text = "".join(b.text for b in resp.content if b.type == "text")
    if not budget:
        text = "<thought_process>\nTIER:" + text
    return strip_thought(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("question", help="the query, or '-' to read stdin")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--judge-model", default="claude-sonnet-5")
    ap.add_argument("--n", type=int, default=3, help="candidates to sample")
    ap.add_argument("--tier", choices=["T0", "T1", "T2"], default="T1",
                    help="effort tier: sets thinking budget and depth")
    ap.add_argument("--critic", action="store_true",
                    help="audit the winner; regenerate once on failure")
    args = ap.parse_args()

    question = sys.stdin.read() if args.question == "-" else args.question
    client = anthropic.Anthropic()

    with ThreadPoolExecutor(max_workers=args.n) as pool:
        candidates = list(pool.map(
            lambda _: sample(client, args.model, question, args.tier),
            range(args.n)))

    numbered = "\n\n".join(f"[{i}]\n{c}" for i, c in enumerate(candidates))
    resp = client.messages.create(
        model=args.judge_model, max_tokens=1024,
        messages=[{"role": "user",
                   "content": JUDGE_PROMPT % (question, numbered)}])
    scores = extract_json(
        "".join(b.text for b in resp.content if b.type == "text"))["scores"]
    totals = {s["index"]: sum(v for k, v in s.items() if k != "index")
              for s in scores}
    winner_idx = max(totals, key=totals.get)
    winner = candidates[winner_idx]
    print(f"[consensus] {args.n} candidates, scores: {totals}, "
          f"winner: [{winner_idx}]", file=sys.stderr)

    if args.critic:
        resp = client.messages.create(
            model=args.judge_model, max_tokens=512,
            messages=[{"role": "user",
                       "content": CRITIC_PROMPT % (question, winner)}])
        verdict = extract_json(
            "".join(b.text for b in resp.content if b.type == "text"))
        if not verdict.get("pass", True):
            print(f"[critic] failures: {verdict['failures']} — regenerating",
                  file=sys.stderr)
            fix = (f"{question}\n\nA prior answer failed audit on: "
                   f"{'; '.join(verdict['failures'])}. Produce a corrected "
                   f"answer that passes.")
            winner = sample(client, args.model, fix, args.tier)

    print(winner)
    return 0


if __name__ == "__main__":
    sys.exit(main())
