#!/usr/bin/env python3
"""
VIVC Photo Downloader

Downloads grape photos from VIVC database and integrates with grape_variety_mapping.jsonl.

USAGE:
# Download photos for a specific VIVC number
python src/vivc_photo_downloader.py --vivc 17638

# Download photos for all varieties with VIVC data
python src/vivc_photo_downloader.py --all

# Test mode (don't download, just show what would be downloaded)
python src/vivc_photo_downloader.py --vivc 17638 --dry-run
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

# Import the grape varieties model and VIVC client
sys.path.insert(0, str(Path(__file__).parent))
from includes.grape_varieties import GrapeVarietiesModel
from includes.vivc_client import fetch_url


@dataclass
class PhotoInfo:
    """Information about a VIVC photo."""
    image_url: str
    download_url: str
    filename: str
    local_path: str
    credits: str
    photo_type: str
    vivc_number: str
    
    def to_dict(self) -> dict:
        return asdict(self)


class VIVCPhotoDownloader:
    """Downloads and manages VIVC grape photos."""
    
    def __init__(self, photos_dir: str = "photos", dry_run: bool = False):
        self.photos_dir = Path(photos_dir)
        self.photos_dir.mkdir(exist_ok=True)
        self.dry_run = dry_run
        self.grape_model = GrapeVarietiesModel()
        
    def fetch_photo_page(self, vivc_number: str) -> str:
        """Fetch the photo page for a specific VIVC number."""
        photo_url = f"https://www.vivc.de/index.php?r=passport/photoviewresult&id={vivc_number}"
        return fetch_url(photo_url)
    
    def extract_photos_from_page(self, html_content: str, vivc_number: str) -> List[PhotoInfo]:
        """Extract photo information from VIVC photo page HTML."""
        photos = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for the photo panels in the photo page
            panels = soup.find_all('div', class_='panel2 panel-default')
            
            for panel in panels:
                panel_title = panel.find('h4', class_='panel-title')
                if panel_title:
                    # Extract photo type from panel title (e.g., "Cluster in the field")
                    title_text = panel_title.get_text()
                    category_match = re.search(r'Category:\s*(.+)', title_text, re.IGNORECASE)
                    photo_type = category_match.group(1).strip() if category_match else None
                    
                    # Find the image in this panel
                    img = panel.find('img')
                    if img and img.get('src'):
                        image_url = img.get('src')
                        
                        # Create filename and local path
                        original_filename = image_url.split('/')[-1] if image_url else None
                        if original_filename:
                            # Create descriptive filename: vivc_number_photo_type_original.jpg
                            safe_type = re.sub(r'[^a-zA-Z0-9]', '_', photo_type or 'unknown')
                            filename = f"vivc_{vivc_number}_{safe_type}_{original_filename}"
                            local_path = str(self.photos_dir / filename)
                            
                            # Get full-size download URL (remove 'k' suffix)
                            download_url = image_url.replace('k.jpg', '.jpg') if image_url.endswith('k.jpg') else image_url
                            
                            # Standard VIVC credits
                            credits = ("Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for "
                                     "Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - "
                                     "76833 Siebeldingen, GERMANY")
                            
                            photo = PhotoInfo(
                                image_url=image_url,
                                download_url=download_url,
                                filename=filename,
                                local_path=local_path,
                                credits=credits,
                                photo_type=photo_type or 'unknown',
                                vivc_number=vivc_number
                            )
                            
                            photos.append(photo)
            
        except Exception as e:
            print(f"Error parsing HTML for VIVC {vivc_number}: {e}")
        
        return photos
    
    def download_photo(self, photo: PhotoInfo) -> bool:
        """Download a single photo to local storage."""
        if self.dry_run:
            print(f"DRY RUN: Would download {photo.download_url} to {photo.local_path}")
            return True
        
        try:
            # Check if file already exists
            if Path(photo.local_path).exists():
                print(f"Photo already exists: {photo.filename}")
                return True
            
            print(f"Downloading {photo.photo_type} photo for VIVC {photo.vivc_number}...")
            
            # Download the image
            response = requests.get(photo.download_url, timeout=30)
            response.raise_for_status()
            
            # Save to local file
            with open(photo.local_path, 'wb') as f:
                f.write(response.content)
            
            print(f"  Saved: {photo.filename} ({len(response.content)} bytes)")
            return True
            
        except requests.RequestException as e:
            print(f"  Error downloading {photo.download_url}: {e}")
            return False
        except Exception as e:
            print(f"  Error saving photo: {e}")
            return False
    
    def update_variety_with_photos(self, variety_name: str, photos: List[PhotoInfo]) -> bool:
        """Update a grape variety with photo information."""
        variety = self.grape_model.get_variety(variety_name)
        if not variety:
            print(f"Warning: Variety '{variety_name}' not found in grape model")
            return False
        
        # Add photos to the portfolio data
        if not variety.portfolio:
            variety.portfolio = {}
        
        if 'photos' not in variety.portfolio:
            variety.portfolio['photos'] = []
        
        # Add new photos (avoid duplicates)
        existing_urls = {p.get('image_url') for p in variety.portfolio['photos']}
        
        for photo in photos:
            if photo.image_url not in existing_urls:
                variety.portfolio['photos'].append({
                    'image_url': photo.image_url,
                    'download_url': photo.download_url,
                    'filename': photo.filename,
                    'local_path': photo.local_path,
                    'credits': photo.credits,
                    'photo_type': photo.photo_type,
                    'vivc_number': photo.vivc_number
                })
        
        return True
    
    def process_variety_by_vivc(self, vivc_number: str) -> List[PhotoInfo]:
        """Process photos for a specific VIVC number."""
        print(f"Processing VIVC {vivc_number}...")
        
        # Fetch photo page
        html_content = self.fetch_photo_page(vivc_number)
        
        if html_content.startswith("❌"):
            print(f"Error fetching photo page: {html_content}")
            return []
        
        # Extract photos
        photos = self.extract_photos_from_page(html_content, vivc_number)
        
        if not photos:
            print(f"No photos found for VIVC {vivc_number}")
            return []
        
        print(f"Found {len(photos)} photos:")
        for photo in photos:
            print(f"  - {photo.photo_type}: {photo.image_url}")
        
        # Download photos
        successful_downloads = []
        for photo in photos:
            if self.download_photo(photo):
                successful_downloads.append(photo)
        
        return successful_downloads
    
    def process_all_varieties_with_vivc(self):
        """Process all varieties that have VIVC data."""
        varieties_with_vivc = []
        
        # Find all varieties with VIVC numbers in their portfolio
        for variety in self.grape_model.get_all_varieties():
            if variety.portfolio and isinstance(variety.portfolio, dict):
                grape_info = variety.portfolio.get('grape', {})
                if isinstance(grape_info, dict):
                    vivc_number = grape_info.get('vivc_number')
                    if vivc_number and vivc_number.strip():
                        varieties_with_vivc.append((variety.name, vivc_number.strip()))
        
        print(f"Found {len(varieties_with_vivc)} varieties with VIVC numbers")
        
        total_photos = 0
        for variety_name, vivc_number in varieties_with_vivc:
            print(f"\n--- Processing {variety_name} (VIVC {vivc_number}) ---")
            photos = self.process_variety_by_vivc(vivc_number)
            
            if photos:
                # Update the variety with photo information
                self.update_variety_with_photos(variety_name, photos)
                total_photos += len(photos)
        
        # Save updated grape model
        if not self.dry_run and total_photos > 0:
            self.grape_model.save_jsonl()
            print(f"\nUpdated grape varieties database with photo information")
        
        print(f"\nTotal photos processed: {total_photos}")
        return total_photos


def main():
    parser = argparse.ArgumentParser(description="Download VIVC grape photos")
    parser.add_argument("--vivc", type=str, help="Specific VIVC number to process")
    parser.add_argument("--all", action="store_true", help="Process all varieties with VIVC data")
    parser.add_argument("--photos-dir", type=str, default="photos", 
                       help="Directory to save photos (default: photos)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without downloading")
    
    args = parser.parse_args()
    
    if not args.vivc and not args.all:
        parser.print_help()
        sys.exit(1)
    
    downloader = VIVCPhotoDownloader(photos_dir=args.photos_dir, dry_run=args.dry_run)
    
    if args.vivc:
        # Process specific VIVC number
        photos = downloader.process_variety_by_vivc(args.vivc)
        print(f"\nProcessed {len(photos)} photos for VIVC {args.vivc}")
        
    elif args.all:
        # Process all varieties with VIVC data
        total_photos = downloader.process_all_varieties_with_vivc()
        print(f"\nTotal photos processed: {total_photos}")


if __name__ == "__main__":
    main()