#!/usr/bin/env python3
"""
Fix Photo Data

Remove redundant VIVC numbers from photo entries in grape_variety_mapping.jsonl
"""

import sys
from pathlib import Path

# Import the grape varieties model
sys.path.insert(0, str(Path(__file__).parent / "src"))
from includes.grape_varieties import GrapeVarietiesModel

def fix_photo_data():
    """Remove redundant vivc_number field from photo entries."""
    grape_model = GrapeVarietiesModel()
    
    changes_made = False
    
    for variety_name, variety in grape_model.varieties.items():
        if variety.portfolio and isinstance(variety.portfolio, dict):
            photos = variety.portfolio.get('photos', [])
            
            for photo in photos:
                if isinstance(photo, dict) and 'vivc_number' in photo:
                    print(f"Removing redundant vivc_number from {variety_name} photo: {photo.get('photo_type')}")
                    del photo['vivc_number']
                    changes_made = True
    
    if changes_made:
        grape_model.save_jsonl()
        print("✅ Fixed photo data - removed redundant VIVC numbers")
    else:
        print("No changes needed")

if __name__ == "__main__":
    fix_photo_data()