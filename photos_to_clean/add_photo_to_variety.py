#!/usr/bin/env python3
"""
Add Photo to Grape Variety

Quick script to add photo information to a specific grape variety.

USAGE:
python src/add_photo_to_variety.py "L'ACADIE BLANC" --vivc 17638
"""

import argparse
import sys
from pathlib import Path

# Import the grape varieties model
sys.path.insert(0, str(Path(__file__).parent))
from includes.grape_varieties import GrapeVarietiesModel

def main():
    parser = argparse.ArgumentParser(description="Add photo to grape variety")
    parser.add_argument("variety_name", help="Name of the grape variety")
    parser.add_argument("--vivc", type=str, required=True, help="VIVC number")
    
    args = parser.parse_args()
    
    # Load grape model
    grape_model = GrapeVarietiesModel()
    
    # Find the variety
    variety = grape_model.get_variety(args.variety_name)
    if not variety:
        print(f"Error: Variety '{args.variety_name}' not found")
        sys.exit(1)
    
    # Add photo information to portfolio
    if not variety.portfolio:
        variety.portfolio = {}
    
    # Add photos section if it doesn't exist
    if 'photos' not in variety.portfolio:
        variety.portfolio['photos'] = []
    
    # Add photo entries
    photos_to_add = [
        {
            'vivc_number': args.vivc,
            'photo_type': 'Cluster in the field',
            'filename': f'vivc_{args.vivc}_Cluster_in_the_field_17107k.jpg',
            'local_path': f'photos/vivc_{args.vivc}_Cluster_in_the_field_17107k.jpg',
            'credits': 'Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY',
            'image_url': f'http://www.vivc.de/gbvp/17107k.jpg',
            'download_url': f'http://www.vivc.de/gbvp/17107.jpg'
        },
        {
            'vivc_number': args.vivc,
            'photo_type': 'Mature leaf',
            'filename': f'vivc_{args.vivc}_Mature_leaf_12774k.jpg',
            'local_path': f'photos/vivc_{args.vivc}_Mature_leaf_12774k.jpg',
            'credits': 'Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY',
            'image_url': f'http://www.vivc.de/gbvp/12774k.jpg',
            'download_url': f'http://www.vivc.de/gbvp/12774.jpg'
        }
    ]
    
    # Add photos to the variety
    for photo_info in photos_to_add:
        variety.portfolio['photos'].append(photo_info)
    
    # Save the updated model
    grape_model.save_jsonl()
    
    print(f"Added {len(photos_to_add)} photos to variety '{args.variety_name}'")
    print(f"Photos saved to grape_variety_mapping.jsonl")
    
    # Show the updated variety info
    print(f"\nVariety: {variety.name}")
    print(f"Photos: {len(variety.portfolio.get('photos', []))}")
    for i, photo in enumerate(variety.portfolio.get('photos', []), 1):
        print(f"  {i}. {photo.get('photo_type')} - {photo.get('filename')}")

if __name__ == "__main__":
    main()