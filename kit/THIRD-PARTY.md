# Excluded and optional third-party components

The starter kit bundles engine-authored orchestration files and skills. The items below are intentionally excluded because they are upstream frameworks, adapters around external packages, client-specific integrations, or optional business modules. Install them separately only when you have a concrete use for them.

| Name | Provenance / URL | How to install |
|---|---|---|
| `algorithmic-art` | Upstream skill with its own complete terms; the bundled `studio-algorithmic-art` process layer expects it when used. | Install the upstream skill into `~/.pi/agent/skills/algorithmic-art/`, then review its license. |
| `copywriting` | Extends `github.com/coreyhaines31/marketingskills` and other upstream writing material. | Obtain the upstream skill separately and review its licenses before adding it. |
| `hyperframes` and `hyperframes-*` | HyperFrames framework documentation and CLI/runtime guidance; see the official HyperFrames project documentation. | Install the HyperFrames skill bundle from its upstream distribution, then add the matching runtime/CLI. |
| `remotion-*` | Remotion framework guidance and examples; official docs: https://www.remotion.dev/docs/ | Install the Remotion skills from the upstream distribution and install the project dependencies they require. |
| `mediabunny` | Mediabunny browser media library; https://mediabunny.dev/ | Install Mediabunny in the project that needs it and add the skill separately. |
| `just-scrape` | ScrapeGraph AI CLI; https://github.com/ScrapeGraphAI/just-scrape | Install with `npm install -g just-scrape`, configure its provider key, then add the skill separately. |
| `watch-skill-video-evidence` | Engine adapter around upstream `watch-skill`; https://github.com/oxbshw/watch-skill | Install the upstream CLI with its documented Python toolchain, then add the adapter separately. |
| `webapp-testing` | Upstream Playwright testing skill with its own complete terms. | Install the upstream skill and Python Playwright according to its documentation. |
| `herdr` | External terminal multiplexer integration; requires the Herdr runtime. | Install Herdr using its official distribution, then add the skill separately. |
| Sensitive payment-provider onboarding skill | Client-specific payment-provider integration with credentials and legal acceptance steps. | Not bundled; use only an independently reviewed integration for your own provider and context. |
| `studio-client-deploy` | Deployment convention tied to a particular business, host, and credential setup. | Define your own deployment policy and runner; do not copy a deployment runner without reviewing it. |

## Excluded binaries and business runners

- `bin/pi` is supplied by the official Pi installation rather than this kit. Install Pi using the official command in `SETUP.md`.
- `bin/fd` and `bin/rg` are platform binaries and are not redistributed. Install `fd` and `ripgrep` from your operating system package manager or their official releases.
- `bin/studio-deploy` is a business-specific deployment runner and is not included. Use your own approved deployment mechanism.

Verify upstream licenses before redistributing any excluded component or adding it to a derivative kit.

The media-use skill's sample audio binaries are omitted from this text-first kit; provide your own licensed media assets when using that skill.
