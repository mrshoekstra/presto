# Deploying the Fable-5 contract outside Claude Code

For direct Messages API integrations (Sonnet 3.5 through Sonnet 5), bind the
contract as the first system block and cache it. The contract is static, so
prompt caching makes its per-request cost one cache read after the first call.

```python
import anthropic
from pathlib import Path

contract = Path("output-styles/fable-5.md").read_text().split("---", 2)[2]

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-5",          # works on claude-3-5-sonnet-latest and newer
    max_tokens=4096,
    temperature=0.2,                  # low variance keeps the register stable
    system=[
        {
            "type": "text",
            "text": contract,
            "cache_control": {"type": "ephemeral"},
        }
    ],
    messages=[{"role": "user", "content": "..."}],
)
```

Deployment rules:

1. **Contract first, task second.** Application-specific instructions go in a
   second system block *after* the contract. Instructions placed before it
   dilute its priority.
2. **Never paraphrase the contract per-request.** Byte-identical text is what
   makes the cache hit; paraphrases also introduce drift between environments.
3. **Long conversations:** re-anchor by appending the guard line (see
   `hooks/payloads/guard.json`) to the latest user turn every 10–15 turns.
   Do not re-send the full contract mid-conversation.
4. **Temperature ceiling:** above ~0.5 the negative constraints start leaking
   (openers reappear first). 0.0–0.3 is the validated band for single-shot
   calls (the consensus runner deliberately samples hotter, then judges).
5. **Prefill forcing (models without native hidden reasoning):** make the
   S2 pipeline stage structurally unavoidable by prefilling the assistant
   turn — append `{"role": "assistant", "content": "<thought_process>\nTIER:"}`
   to `messages`. The model must complete the precompute block before it can
   reach answer text. Strip everything through `</thought_process>` before
   display.
6. **Extended thinking (Claude models):** map the intake tier to a real
   thinking budget instead of the default — e.g. T0: thinking off,
   T1: `{"type": "enabled", "budget_tokens": 4000}`, T2: 16000+. With
   thinking enabled, omit the prefill (S2 runs in the native channel) and
   note the API requires temperature 1 with thinking on — the judge stage
   below replaces the low-temperature stability lever.
