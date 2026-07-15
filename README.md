# Fable-5 Emulation Plugin
<!-- DESCRIPTION START -->
A Claude Code plugin that replaces the default assistant register on Sonnet-class models with the Fable-5 cognitive framework: three-chamber reasoning, outcome-first structured output, and zero-drift behavioral constraints.
<!-- DESCRIPTION END -->

## Architecture

| Component | Path | Role |
|---|---|---|
| Manifest | `.claude-plugin/plugin.json` | Plugin identity and metadata |
| Behavioral contract | `output-styles/fable-5.md` | The core system-prompt payload (output style) |
| Subagent | `agents/fable-architect.md` | Contract-bound specialist for design/decomposition tasks |
| Zero-drift hooks | `hooks/hooks.json`, `hooks/inject-contract.sh` | Full contract on SessionStart; ~40-token guard on every prompt |
| Manual re-arm | `commands/fable.md` | `/fable` — recover from register drift mid-session |
| API deployment | `docs/api-deployment.md` | Binding the contract via the Messages API with prompt caching |

## Installation

```
/plugin marketplace add mrshoekstra/presto
/plugin install fable-5-emulation@presto
```

## Activation by surface

The contract has three binding mechanisms; which one applies depends on where
you run Claude. Availability of `/output-style` is NOT required — the hooks
are the primary binding.

| Surface | Binding mechanism | Action needed after install |
|---|---|---|
| Claude Code CLI | Hooks (+ output style where supported) | None — SessionStart hook binds the contract in every new session |
| VS Code / JetBrains extension | Hooks | None — same as CLI; `/fable` re-arms manually |
| Claude Desktop / claude.ai chat | Project instructions | Plugins don't run here. Paste the body of `output-styles/fable-5.md` into a Project's custom instructions (or a custom Style) |
| Direct Messages API | Cached system block | See `docs/api-deployment.md` |

To verify the contract is bound, ask "what model are you?" — the reply should
be verdict-first and name the real underlying model plus the framework. A
"Great question!" opener or a "Let me know if…" closer means it is not bound;
run `/fable` to re-arm.

## Design constraints

The contract overrides register, structure, and reasoning discipline. It
deliberately does **not** alter the underlying model's safety behavior or
instruct it to misrepresent its identity — wrappers that attempt either are
unstable and drift. See `<invariants>` in the contract.
<!--
## 📑 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Support](#support)
- [License](#license)

## ✨ Features
- 
- 
- 

## 📋 Prerequisites

## 🛠️ Installation

## ⚙️ Configuration

## 🚀 Usage

## 🧪 Tests

## 🚢 Deployment

## 🤝 Contributing

## 🛡️ Security

## 👥 Authors / Maintainers

-->
## ❤️ Support

If this project saved you some time, please consider giving it a ⭐ **Star** on GitHub; it helps others discover the repository!

If you would like to support my work further, please check out the **Sponsor this project** section on this repository page. Even a small contribution makes a big difference!

## ⚖️ License

Distributed under the [MIT License](LICENSE.md).
