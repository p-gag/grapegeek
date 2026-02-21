#!/usr/bin/env python3
"""
Test script for extracting VIVC grape photos and credits.
"""

import requests
import urllib.parse
import os
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass, asdict
from typing import Optional, List
import sys

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from includes.vivc_client import fetch_passport_page, fetch_url

@dataclass
class PhotoInfo:
    """Information about a VIVC photo."""
    image_url: str
    download_url: str
    filename: str
    credits: Optional[str] = None
    photo_type: Optional[str] = None  # e.g., "Cluster in the field"
    
    def to_dict(self) -> dict:
        return asdict(self)

def extract_photos_from_passport(html_content: str, vivc_number: str) -> List[PhotoInfo]:
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
                    
                    # Extract the photo ID from the onclick handler
                    onclick = img.get('onclick', '')
                    photo_id_match = re.search(r'showFoto2\((\d+),', onclick)
                    photo_id = photo_id_match.group(1) if photo_id_match else None
                    
                    # Create filename from URL
                    filename = image_url.split('/')[-1] if image_url else None
                    
                    # For credits, we know from the screenshot that they are available in the modal
                    # The standard VIVC credit format based on the metadata found in the HTML
                    credits = ("Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, "
                              "Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY")
                    
                    photo = PhotoInfo(
                        image_url=image_url,
                        download_url=image_url.replace('k.jpg', '.jpg') if image_url else '',  # Remove 'k' for full size
                        filename=filename,
                        credits=credits,
                        photo_type=photo_type
                    )
                    
                    photos.append(photo)
                    print(f"Extracted photo: {photo_type} - {image_url}")
        
        # Also look for general structure info
        print(f"\n=== FOUND {len(photos)} PHOTOS ===")
        
    except Exception as e:
        print(f"Error parsing HTML: {e}")
    
    return photos

def fetch_photo_page(vivc_number: str) -> str:
    """Fetch the photo page for a specific VIVC number."""
    photo_url = f"https://www.vivc.de/index.php?r=passport/photoviewresult&id={vivc_number}"
    return fetch_url(photo_url)

def test_photo_extraction(vivc_number: str):
    """Test photo extraction for a specific VIVC number."""
    print(f"Testing photo extraction for VIVC {vivc_number}")
    print("=" * 50)
    
    # First fetch the passport page to confirm it has photos
    passport_html = fetch_passport_page(vivc_number)
    
    if passport_html.startswith("❌"):
        print(f"Error fetching passport page: {passport_html}")
        return
    
    print(f"Passport HTML fetched successfully, length: {len(passport_html)}")
    
    # Now fetch the photo page
    photo_html = fetch_photo_page(vivc_number)
    
    if photo_html.startswith("❌"):
        print(f"Error fetching photo page: {photo_html}")
        return
    
    print(f"Photo HTML fetched successfully, length: {len(photo_html)}")
    
    # Save photo HTML for inspection
    photo_file = Path(f"debug_vivc_{vivc_number}_photos.html")
    with open(photo_file, 'w', encoding='utf-8') as f:
        f.write(photo_html)
    print(f"Photo HTML saved to: {photo_file}")
    
    # Extract photos from the photo page
    photos = extract_photos_from_passport(photo_html, vivc_number)
    
    print(f"\nFound {len(photos)} photos")
    for i, photo in enumerate(photos, 1):
        print(f"Photo {i}: {json.dumps(photo.to_dict(), indent=2)}")

if __name__ == "__main__":
    # Test with L'Acadie Blanc (VIVC 17638)
    test_photo_extraction("17638")