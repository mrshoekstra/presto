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
| Zero-drift hooks | `hooks/hooks.json`, `hooks/payloads/` | Full contract on SessionStart; ~40-token guard on every prompt. Payloads are pre-built by `hooks/build-payloads.sh`; runtime is a bare `cat` |
| Manual re-arm | `commands/fable.md` | `/fable` — recover from register drift mid-session |
| Decomposition skill | `skills/fable-chambers/` | Visible three-chamber pass: assumption ledger, scope contract, hostile refinement — auto-triggers on complex/ambiguous tasks |
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

## Troubleshooting: hooks not firing

Hooks fail silently — if the SessionStart injection isn't working you just get
default behavior. Checklist, in order:

1. **Update, then reload.** Marketplace installs do not update when the repo
   changes: run `/plugin marketplace update presto`, then
   `/plugin update fable-5-emulation`, then `/reload-plugins` (or start a new
   session — hooks load at session startup).
2. **Check registration:** run `/hooks` — the plugin's SessionStart and
   UserPromptSubmit entries should be listed. If they're absent, the plugin's
   hooks were never loaded (see 1).
3. **Windows (native):** shell-form hook commands run in Git Bash when Git for
   Windows is installed, otherwise PowerShell — both support `cat`, and
   `${CLAUDE_PLUGIN_ROOT}` is substituted by Claude Code itself, so the
   current hooks are Windows-compatible. Plugin versions before v1.1.0 used a
   bash+python3 script that cannot run on native Windows — update per step 1.
4. **Hookless fallback (any OS):** paste the contract body from
   `output-styles/fable-5.md` into your user-level CLAUDE.md
   (`~/.claude/CLAUDE.md`; on Windows `%USERPROFILE%\.claude\CLAUDE.md`) —
   loaded in every CLI and IDE-extension session with no hook machinery.
   `/fable` remains the manual re-arm.

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
