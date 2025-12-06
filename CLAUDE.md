# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Running the Application
```bash
# Generate a technical article for a grape variety
python main.py grape <variety_name> --type technical

# Generate winemaking stories for a grape variety  
python main.py grape <variety_name> --type story

# Research grape varieties in a region
python main.py region <region_name>

# Dry run (show prompts without calling OpenAI)
python main.py grape <variety_name> --dry-run
python main.py region <region_name> --dry-run
```

### Dependencies
```bash
# Install dependencies using uv (preferred)
uv sync

# Or install with pip
pip install -e .
```

### Environment Setup
- Requires `OPENAI_API_KEY` environment variable (uses OpenAI Responses API with web_search tools)
- Uses `.env` file for environment variables

## Project Architecture

### Core Structure
This is an AI-powered content generation system for creating magazine-style articles about cold-climate grape varieties, focused on hybrid grapes in northeastern US and eastern Canada.

**Main Components:**
- `main.py`: CLI entry point with subcommands for grape articles and region research
- `src/grapegeek/base.py`: BaseGenerator class with shared OpenAI integration and file handling
- `src/grapegeek/grape_article_generator.py`: GrapeArticleGenerator for variety-specific content
- `src/grapegeek/region_researcher.py`: RegionResearcher for regional variety discovery

### Prompt System Architecture
The application uses a layered prompt system:

1. **General Prompts** (`prompts/general/`): System-wide instructions for tone, citation style
2. **Content-Type Prompts** (`prompts/grapes/`): 
   - `technical_prompt.md`: Comprehensive technical analysis template
   - `art_prompt.md`: Winemaking story and narrative template
3. **Entity Context** (`prompts/grapes/articles/`, `prompts/regions/`): 
   - YAML frontmatter files with variety/region-specific context
   - Prevents AI confusion by providing precise identification context

### OpenAI Integration
- Uses OpenAI Responses API with `gpt-5` model
- Includes `web_search` tool for real-time research and citation gathering
- All API calls go through `BaseGenerator.call_openai()` method
- Dry run mode shows full prompt structure and debug information without API calls

### Output Organization
- `output/articles/`: Generated grape variety articles
  - Technical: `{variety_name}.md` 
  - Stories: `{variety_name}_winemaking_stories.md`
- `output/regions/`: Regional research results as `{region_name}_varieties.md`
- `debug/`: Dry run outputs with `_debug.md` suffix

### Variety Context System
Each grape variety can have a context file at `prompts/grapes/articles/{variety_name}.md` with YAML frontmatter:
```yaml
---
name: "Official Variety Name"
prompt: "Minimal context to avoid confusion with similarly named varieties"
---
```

### Region Context System  
Each region can have a context file at `prompts/regions/{region_name}.md` with YAML frontmatter:
```yaml
---
name: "Region Name"
summary: "Brief regional description"
known_varieties: "List of known varieties"
trade_association: "Association name"
trade_association_url: "URL"
---
```

## Development Notes

### File Handling Patterns
- All file operations use `pathlib.Path` 
- YAML frontmatter parsing handles missing files gracefully with defaults
- Output directories are created automatically

### Error Handling
- OpenAI API errors are caught and returned as error strings
- Missing prompt files return empty strings rather than failing
- Dry run mode provides comprehensive debugging without API calls

### Code Organization
- Shared functionality is in `BaseGenerator` base class
- Generator classes inherit common file operations and OpenAI integration
- CLI uses argparse with subcommands for different content types