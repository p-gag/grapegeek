#!/usr/bin/env python3
"""
Sync French translations for GrapeGeek Next.js site.

Reads messages/en.json as source of truth, compares with stored hashes in
messages/fr.hashes.json, and translates only changed/new keys via OpenAI.

Usage:
    python scripts/sync_nextjs_french.py          # Translate changed keys
    python scripts/sync_nextjs_french.py --dry-run # Show what would be translated
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
EN_JSON = REPO_ROOT / "messages" / "en.json"
FR_JSON = REPO_ROOT / "messages" / "fr.json"
FR_HASHES = REPO_ROOT / "messages" / "fr.hashes.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------------------
# OpenAI translation
# ---------------------------------------------------------------------------
def translate_with_openai(keys_to_translate: dict[str, str]) -> dict[str, str]:
    """Call OpenAI to translate a batch of key-value pairs."""
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai package not installed. Run: pip install openai")
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    prompt = (
        "Translate the following UI strings from English to French for a Quebec wine growing website.\n\n"
        "Rules:\n"
        "- Use Quebec French where appropriate\n"
        "- Keep a friendly, approachable tone\n"
        "- Preserve all {variable} placeholders exactly as-is — do not translate content inside {}\n"
        "- Variable names like {variety}, {winegrower}, {count} are code placeholders\n"
        "- Grape variety names inside {variety} are proper nouns and must NOT be translated\n"
        "- Keep technical viticulture terms accurate\n"
        "- For plural forms (.one/.other suffixes), maintain the same plural logic\n\n"
        "Return a JSON object with the same keys and French translated values.\n\n"
        f"Strings to translate:\n{json.dumps(keys_to_translate, indent=2, ensure_ascii=False)}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional translator specializing in Quebec French for wine industry websites. Always return valid JSON."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    result_text = response.choices[0].message.content
    return json.loads(result_text)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Sync French translations for GrapeGeek Next.js")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be translated without calling OpenAI")
    args = parser.parse_args()

    # Load files
    en = load_json(EN_JSON)
    fr = load_json(FR_JSON)
    hashes = load_json(FR_HASHES)

    if not en:
        print(f"ERROR: {EN_JSON} not found or empty.")
        sys.exit(1)

    # Determine what needs translation
    to_translate: dict[str, str] = {}
    to_delete: list[str] = []
    unchanged: list[str] = []

    for key, en_value in en.items():
        current_hash = sha256(en_value)
        stored_hash = hashes.get(key)

        if stored_hash == current_hash and key in fr:
            unchanged.append(key)
        else:
            to_translate[key] = en_value

    # Find keys to delete (in fr.json but not in en.json)
    for key in list(fr.keys()):
        if key not in en:
            to_delete.append(key)

    # Report
    print(f"Translation status:")
    print(f"  Unchanged:  {len(unchanged)}")
    print(f"  To translate (new/changed): {len(to_translate)}")
    print(f"  To delete (removed from en.json): {len(to_delete)}")

    if args.dry_run:
        if to_translate:
            print(f"\nWould translate {len(to_translate)} keys:")
            for key in list(to_translate.keys())[:20]:
                print(f"  - {key}: {to_translate[key][:60]}...")
            if len(to_translate) > 20:
                print(f"  ... and {len(to_translate) - 20} more")
        if to_delete:
            print(f"\nWould delete {len(to_delete)} keys from fr.json:")
            for key in to_delete:
                print(f"  - {key}")
        print("\nDry run complete. No changes made.")
        return

    # Perform translation
    if to_translate:
        print(f"\nTranslating {len(to_translate)} keys with OpenAI...")
        translated = translate_with_openai(to_translate)

        # Update fr.json and hashes
        for key, fr_value in translated.items():
            fr[key] = fr_value
            hashes[key] = sha256(en[key])  # Store hash of English source value

        print(f"  Translated {len(translated)} keys successfully")
    else:
        print("\nNo keys need translation.")

    # Delete removed keys
    if to_delete:
        for key in to_delete:
            del fr[key]
            hashes.pop(key, None)
        print(f"Deleted {len(to_delete)} obsolete keys")

    # Save updated files
    save_json(FR_JSON, fr)
    save_json(FR_HASHES, hashes)

    print(f"\nSaved {FR_JSON}")
    print(f"Saved {FR_HASHES}")
    print("Done!")


if __name__ == "__main__":
    main()
