# Grape Geek Directory Structure

## Project Layout

```
grapegeek/
├── prompts/                    # All prompt templates
│   ├── general/               # General system prompts
│   └── grapes/                # Grape-specific prompts
│       ├── article_prompt.md  # Shared article generation template
│       └── articles/          # Individual variety contexts
├── output/                    # Generated content
│   ├── articles/              # Final grape articles
│   └── citations/             # Citation databases
├── templates/                 # Article templates
├── src/grapegeek/            # Source code
└── main.py                   # Main entry point
```

## Prompt System

### General Prompts (`prompts/general/`)
- `system_prompt.md` - Overall system instructions for AI
- `citation_style.md` - Citation format requirements
- `tone_guidelines.md` - Writing style and tone instructions

### Grape-Specific Prompts (`prompts/grapes/`)
- `article_prompt.md` - Shared prompt template loaded for all article generation

### Individual Variety Context (`prompts/grapes/articles/`)
Individual YAML frontmatter files for each grape variety:
- **Format**: `{grape_name}.md` with YAML header
- **Fields**:
  - `name`: Official grape variety name
  - `prompt`: Variety-specific context to avoid ambiguity
- **Example**: `itasca.md` contains minimal context for Itasca variety
- **Purpose**: Provide just enough context to identify the variety correctly

## Output Structure

### Articles (`output/articles/`)
- `{grape_name}.md` - Complete generated articles
- `{grape_name}_draft.md` - Work-in-progress versions

### Citations (`output/citations/`)
- `{grape_name}_sources.json` - Structured citation database
- `bibliography.md` - Master bibliography across all grapes