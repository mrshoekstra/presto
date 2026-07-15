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

Add this repository as a plugin source, install `fable-5-emulation`, then select
the `Fable-5` output style (`/output-style fable-5`). The SessionStart hook also
binds the contract automatically, so the framework is active even before the
output style is selected.

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
