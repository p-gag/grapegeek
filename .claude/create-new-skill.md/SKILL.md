---
name: create-new-skill
description: >
  Use this skill when you need to design or generate a new Claude Skill for a specific, well-defined task:
  it specifies folder layout, SKILL.md format, and how to keep skills focused and routable.
---

## Create New Skill

Use this whenever a user says “create/make a skill for X” or wants a workflow turned into a Claude Skill.

### 1. Scope

- One clear responsibility per skill.
- If multiple unrelated jobs are requested, propose multiple skills.
- Avoid vague “do everything” scopes.

### 2. Folder Layout

Use a kebab-case slug (a–z, 0–9, `-`), e.g. `support-email-drafter`:

- Local / Claude Code / SDK:
  - `.claude/skills/<skill-slug>/SKILL.md`
- API/org-level (to zip & upload):
  - `<skill-slug>/SKILL.md`

Optional (recommended for non-trivial skills):

- `resources/` — policies, style guides, schemas.
- `templates/` — reusable output skeletons.
- `scripts/` — small deterministic helpers (no secrets).

### 3. SKILL.md Structure

Always start with YAML frontmatter:

- `name`: same as folder slug.
- `description`:
  - 1–3 sentences.
  - Must say:
    - **What** the skill does.
    - **When** to use it (“Use when …”).

Then body:

#### `## <Human Title>`

- Short human-readable name.

#### `## Instructions`

- Bullet/step format.
- Explicitly define:
  - Inputs (e.g. `user_query`, `source_docs`, `config`).
  - Procedure (5–15 precise steps).
  - Output format (Markdown, JSON schema, etc.).
  - Boundaries (what not to do, when to defer).

#### `## Examples`

- 1–3 concise examples:
  - Trigger situation.
  - Expected behavior / output style.
- Keep aligned with Instructions.

### 4. Progressive Detail & Safety

- Keep `SKILL.md` compact.
- Put long refs in `resources/` and `templates/`, and reference them explicitly.
- No credentials, private tokens, or dangerous “run arbitrary remote code” behavior.
- Optimize `description` for routing with clear keywords + “Use when …”.

---

## Example: Generated Skill Start

When asked to build a new skill, start like this:

```md
---
name: the-skill
description: >
  Use this skill when you need to <concise purpose>. It should be used when <clear trigger conditions>.
---

## The Skill

## Instructions
- Describe required inputs (…)
- Step-by-step process (…)
- Exact output format (…)

## Examples
- Example trigger + expected response outline.
