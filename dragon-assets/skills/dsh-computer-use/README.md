# DSH Computer Use

[![X (Twitter)](https://img.shields.io/badge/-@anion__ex-000000?style=flat-square&logo=x&logoColor=white)](https://x.com/anion_ex)
[![License: MIT](https://img.shields.io/badge/license-MIT-2f855a.svg)](LICENSE)
![macOS](https://img.shields.io/badge/macOS-14%2B-111827.svg)
![Universal binary](https://img.shields.io/badge/native-arm64%20%2B%20x86__64-2563eb.svg)
![DeepSeek Harness](https://img.shields.io/badge/DeepSeek%20Harness-Bundle-5b50ed.svg)

**Native macOS control for DeepSeek Harness that keeps your real cursor and foreground application alone by default; the Bundle may bring the target app forward before keyboard input for reliable typing.**

DSH Computer Use gives an Agent fresh Accessibility observations, exact process/window targeting, stale-state rejection, scoped application access, and verified post-action state. Semantic Accessibility comes first; mouse, drag, wheel, and keyboard fallback are routed to the selected process instead of the global desktop.

---

## Quick start (verbatim from upstream)

### Prerequisites

- macOS 14 or newer.
- DeepSeek Harness with a Web or Headless Profile and the Skill Tool mounted.
- macOS Accessibility permission for observation and native actions.
- macOS Screen Recording permission only when a screenshot is requested.
- Node.js `^22.19.0` or `>=24.0.0` when building this repository.

Install the Web and Headless bundles directly from npm:

> [!IMPORTANT]
> The published package name is `@anionex/dsh-computer-use`. The former
> `@dsh-external/dsh-computer-use` name was never published to npm and is not
> installable; update any old profile or manifest references before installing.

```sh
dsh plugin --profile web add @anionex/dsh-computer-use
dsh plugin --profile headless add @anionex/dsh-computer-use

dsh --profile web --dump-config | grep computer-use
dsh --profile headless --dump-config | grep computer-use
```

For local development, replace the package name with an absolute checkout path.

Restart a running `dsh web` host after changing the installed plugin, then start a new Session so the host reloads the Bundle and Skill catalog.

Load the Skill in that Session:

```text
/computer-use
```

---

## Status

- early `0.1.0`; model-facing and provider behavior may change before a stable release.
- The current provider is **macOS-only**. Windows UI Automation and Linux providers are not implemented.
- On non-macOS hosts the plugin degrades gracefully: the DSH profile starts normally, Computer Use Tools and the Skill are not registered, and Web Settings reports `COMPUTER_UNSUPPORTED_PLATFORM` instead of failing startup.

---

## License

[MIT](LICENSE) © 2026 anionex.

---

## Upstream / Modified by

- Upstream: https://github.com/Anionex/dsh-computer-use
- Modified by: dragon-engine / user老李 / 2026-08-23
- Reason: integrate as stage 26 skill bundle for DSH ecosystem
- License integrity: LICENSE file preserved verbatim (MIT); only added "Modified by" footer