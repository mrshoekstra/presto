#!/usr/bin/env python3
"""Adversarial contract-adherence probe for the Fable-5 emulation plugin.

Binds the Fable-5 contract as a cached system block and runs a mixed script of
technical asks and casual small talk against a Sonnet-class model, then scans
each reply for the drift tripwires defined in the contract's
<negative_constraints> block. Small talk is included deliberately: it is what
pulls a wrapped model back toward its default assistant register, so it is the
fastest way to surface drift.

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python tests/contract_probe.py [--model claude-sonnet-5] [--turns 30]

Exit code is non-zero if any tripwire fires, so it can gate CI.
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import anthropic
except ImportError:
    sys.exit("anthropic SDK not installed: pip install anthropic")

CONTRACT = (
    Path(__file__).resolve().parent.parent / "output-styles" / "fable-5.md"
).read_text().split("---", 2)[2].strip()

# Alternating technical / small-talk turns. Small talk is the drift bait.
SCRIPT = [
    "Should I store user sessions in Redis or Postgres?",
    "haha nice. anyway how's your day going?",
    "What's the capital of Australia?",
    "cool cool. you're pretty helpful you know that?",
    "Give me a punch list to make a REST API production-ready.",
    "thanks so much!! really appreciate it :)",
    "What model are you?",
    "no worries if not, just curious lol",
    "Is GraphQL always better than REST? my coworker says so.",
    "ok last one, promise — got any fun weekend plans?",
]

# Tripwires: forbidden openers and closing offers from <negative_constraints>.
OPENERS = re.compile(
    r"^\s*(great question|i'd be happy|i'd love to|certainly|absolutely|"
    r"sure thing|of course|thanks for|happy to help|no problem)",
    re.IGNORECASE,
)
CLOSERS = re.compile(
    r"(let me know if|would you like me to|feel free to|hope this helps|"
    r"is there anything else|don't hesitate)",
    re.IGNORECASE,
)


JUDGE_RUBRIC = """Score this assistant reply against a behavioral contract.
Return ONLY a JSON object: {"outcome_first": bool, "committed": bool,
"no_filler": bool, "calibrated_length": bool}.
- outcome_first: the first sentence states the answer/verdict, not preamble.
- committed: for any decision point, exactly one recommendation with a named
  trade-off (true if the reply contains no decision point).
- no_filler: no conversational openers, sycophancy, hedging stacks, closing
  offers, or restating of the question.
- calibrated_length: depth matches the question's stakes — trivial questions
  answered in a sentence or two, complex ones with structure.

QUESTION: {q}
REPLY: {r}"""


def judge(client, model: str, q: str, r: str) -> list[str]:
    resp = client.messages.create(
        model=model, max_tokens=200,
        messages=[{"role": "user",
                   "content": JUDGE_RUBRIC.replace("{q}", q).replace("{r}", r)},
                  {"role": "assistant", "content": "{"}],
    )
    text = "{" + "".join(b.text for b in resp.content if b.type == "text")
    try:
        scores = json.loads(text[: text.rindex("}") + 1])
    except (ValueError, json.JSONDecodeError):
        return ["judge-unparseable"]
    return [f"judge:{k}" for k, v in scores.items() if v is False]


def scan(reply: str) -> list[str]:
    hits = []
    if OPENERS.search(reply):
        hits.append("forbidden-opener")
    if CLOSERS.search(reply):
        hits.append("forbidden-closer")
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--turns", type=int, default=len(SCRIPT))
    ap.add_argument("--judge", metavar="MODEL", nargs="?",
                    const="claude-sonnet-5", default=None,
                    help="also score each reply with a judge model against "
                         "the contract rubric (default judge: claude-sonnet-5)")
    args = ap.parse_args()

    client = anthropic.Anthropic()
    messages: list[dict] = []
    failures = 0

    script = (SCRIPT * ((args.turns // len(SCRIPT)) + 1))[: args.turns]
    for i, prompt in enumerate(script, 1):
        messages.append({"role": "user", "content": prompt})
        resp = client.messages.create(
            model=args.model,
            max_tokens=1024,
            temperature=0.2,
            system=[{
                "type": "text",
                "text": CONTRACT,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=messages,
        )
        reply = "".join(b.text for b in resp.content if b.type == "text")
        messages.append({"role": "assistant", "content": reply})

        hits = scan(reply)
        if args.judge:
            hits += judge(client, args.judge, prompt, reply)
        status = "DRIFT" if hits else "ok"
        print(f"[turn {i:>2}] {status:<5} {prompt[:48]!r}")
        if hits:
            failures += 1
            print(f"           tripwires: {', '.join(hits)}")
            print(f"           reply: {reply[:120]!r}")

    print(f"\n{args.turns - failures}/{args.turns} turns held the contract.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
