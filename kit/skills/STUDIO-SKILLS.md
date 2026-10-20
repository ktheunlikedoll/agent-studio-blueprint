---
name: studio-skills-guide
description: "Internal documentation on how to curate per-agent skills in the studio. Not an invokable skill."
disable-model-invocation: true
---

# Studio skills — how to curate per-agent skills

Every studio agent is created with `inheritSkills: false`, so it starts with **no** skills and gets only the ones you explicitly attach. This lets you curate a specialized skill set per role.

## How to attach a skill to a studio agent

1. **Create the skill.** Make a directory under a discovered skills path containing a `SKILL.md`:

   ```
   ~/.pi/agent/skills/<skill-name>/SKILL.md
   ```

   The directory name is the skill name. A minimal `SKILL.md`:

   ```markdown
   ---
   name: <skill-name>
   description: One line describing when this skill applies.
   ---

   # <Skill name>

   Specialized instructions the agent should follow when this skill is loaded...
   ```

   Discovered skill paths (recursive): `~/.pi/agent/skills/`, `~/.agents/skills/`, `.pi/skills/`, `.agents/skills/`.

2. **Wire it to the agent.** Open the agent file, e.g. `~/.pi/agent/agents/studio/ui-designer.md`, and add a `skills:` field to the frontmatter:

   ```yaml
   skills:
     - studio-design-tokens
     - studio-accessibility
   ```

3. **Reload.** Restart Pi (or run `/subagents-doctor`) so discovery picks up the new skill.

## Current per-agent skill mapping

This is the live mapping set in each agent's `skills:` frontmatter field. Edit the agent file to change it.

| Agent | Attached skills |
|---|---|
| `studio.researcher` | `just-scrape`, `studio-research-method` |
| `studio.scout` | `librarian`, `studio-recon` |
| `studio.developer` | `webapp-testing`, `studio-tdd-method`, `studio-backend-standards`, `studio-environment`, `remotion-saas`, `remotion-render`, `mediabunny` |
| `studio.ui-designer` | `high-end-visual-design`, `data-visualization`, `accessibility`, `tailwind-design-system`, `design-handoff`, `copywriting`, `studio-design-language`, `studio-vectors`, `studio-image-gen`, `studio-pexels`, `studio-environment` |
| `studio.layout-designer` | `studio-design-language`, `canvas-design`, `ppt-visual`, `studio-editorial-grid`, `studio-vectors`, `studio-image-gen`, `studio-pexels`, `studio-environment` |
| `studio.motion-designer` | `hyperframes`, `design-motion-principles`, `studio-design-language`, `studio-vectors`, `studio-image-gen`, `studio-pexels`, `studio-environment`, `remotion-best-practices`, `remotion-create`, `remotion-markup`, `remotion-render` |
| `studio.generative-designer` | `algorithmic-art`, `studio-algorithmic-art`, `studio-vision-critique`, `studio-design-language`, `studio-environment` |
| `studio.critic` | `studio-critique`, `studio-copy-critique`, `studio-vision-critique`, `studio-design-language`, `accessibility`, `copywriting` |
| `studio.strategist` | `studio-design-language`, `studio-editorial-grid`, `high-end-visual-design`, `studio-task-decomposition`, `studio-environment` |
| `studio.tech-director` | `studio-grill`, `studio-task-decomposition`, `studio-environment` |
| `studio.art-director` | `studio-critique`, `copywriting`, `studio-design-language`, `studio-environment` |
| `minion` | `inheritSkills: true` (inherits the parent's available skills) |
| `git-committer` | `inheritSkills: false`, no skills attached |
| `oracle` (builtin, pinned) | `studio-grill`, `studio-critique`, `studio-design-language`, `studio-copy-critique`, `studio-task-decomposition`, `accessibility` (set via `subagents.agentOverrides.oracle.skills`) |
| `reviewer` (builtin, pinned) | inherit builtin defaults; no per-agent skills attached |

To add or change a skill, edit the agent's `skills:` field in `~/.pi/agent/agents/<agent>.md` (or `~/.pi/agent/agents/studio/<agent>.md`), then run `/subagents-doctor` to reload.
