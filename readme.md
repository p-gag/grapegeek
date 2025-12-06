# Grape Geek

Welcome to **Grape Geek**! 🍇

This repository contains the source code and content generation system for the Grape Geek project.

## Quick Start

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

### Setup
```bash
# Install dependencies using uv (preferred)
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY
```

## Project Files

- **`about.md`** - Project description and philosophy (suitable for MkDocs documentation)
- **`technical_documentation.md`** - Technical details for content generation process
- **`CLAUDE.md`** - Developer guidance for Claude Code
- **`STRUCTURE.md`** - Directory structure and organization

## Contributing

This is a personal project focused on hybrid grapes in cold climates. See `about.md` for the project philosophy and approach.
