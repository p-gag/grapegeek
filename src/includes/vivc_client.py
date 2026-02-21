#!/usr/bin/env python3
"""
VIVC Client Module

Unified client for VIVC search and passport operations with JSONL caching.
"""

import argparse
import sys
import requests
import urllib.parse
import os
import json
import hashlib
import time
from pathlib import Path
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import Optional, List
import re


# Cache file path
CACHE_FILE = Path("data/vivc_cache.jsonl")


@dataclass
class GrapeId:
    """Grape identifier with name and VIVC number."""
    name: Optional[str] = None
    vivc_number: Optional[str] = None
    
    def __str__(self) -> str:
        if self.name and self.vivc_number:
            return f"{self.name} ({self.vivc_number})"
        elif self.name:
            return self.name
        elif self.vivc_number:
            return f"VIVC {self.vivc_number}"
        else:
            return "Unknown"


@dataclass
class PassportData:
    """Structured passport data for a grape variety."""
    grape: GrapeId
    berry_skin_color: Optional[str] = None
    country_of_origin: Optional[str] = None
    species: Optional[str] = None
    parent1: Optional[GrapeId] = None
    parent2: Optional[GrapeId] = None
    sex_of_flower: Optional[str] = None
    number_of_photos: Optional[str] = None
    year_of_crossing: Optional[str] = None
    synonyms: Optional[list[str]] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON format."""
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class VarietySearchResult:
    """Search result for a grape variety."""
    cultivar_name: Optional[str] = None
    prime_name: Optional[str] = None
    vivc_number: Optional[str] = None
    species: Optional[str] = None
    berry_skin_color: Optional[str] = None
    country_of_origin: Optional[str] = None
    passport_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON format."""
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class PhotoCredit:
    """Photo credit information from VIVC foto2 modal."""
    note: Optional[str] = None  # The usage note (e.g., "Please note: This photo can be reproduced...")
    credit: Optional[str] = None  # The actual credit (e.g., "Ursula Brühl, Julius Kühn-Institut...")

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON format."""
        return json.dumps(self.to_dict(), indent=indent)


class VIVCCache:
    """JSONL cache for VIVC responses."""
    
    def __init__(self, cache_file: Path = CACHE_FILE):
        self.cache_file = cache_file
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self._cache = self._load_cache()
    
    def _load_cache(self) -> dict:
        """Load cache from JSONL file."""
        cache = {}
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            cache[entry['url']] = entry['content']
            except Exception:
                # If cache is corrupted, start fresh
                pass
        return cache
    
    def _save_entry(self, url: str, content: str):
        """Append entry to JSONL file."""
        entry = {
            'url': url,
            'content': content,
            'timestamp': json.dumps(None)  # Could add timestamp if needed
        }
        
        with open(self.cache_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get(self, url: str) -> Optional[str]:
        """Get content from cache."""
        return self._cache.get(url)
    
    def set(self, url: str, content: str):
        """Set content in cache."""
        if url not in self._cache:
            self._cache[url] = content
            self._save_entry(url, content)


# Global cache instance
_cache = VIVCCache()


def fetch_url(url: str, max_retries: int = 3, retry_delay: float = 10.0, delay: float = 3.0, progressive_delay: bool = True) -> str:
    """Fetch URL with caching, throttling, and retry logic.

    Args:
        url: URL to fetch
        max_retries: Maximum number of retry attempts for timeouts/504 errors
        retry_delay: Base delay in seconds between retries (increases with each retry)
        delay: Delay in seconds before making request (default: 3.0, only applies to non-cached)
        progressive_delay: If True, increase delay exponentially on timeouts (default: True)

    Returns:
        Raw HTML content or error message
    """
    # Check cache first
    cached_content = _cache.get(url)
    if cached_content:
        return cached_content

    # Making actual request - inform user and throttle
    print(f"   → VIVC request (not cached), waiting {delay}s...")
    time.sleep(delay)

    last_error = None

    for attempt in range(max_retries):
        try:
            # Increase timeout progressively for slow VIVC server
            timeout = 60 if not progressive_delay else 60 + (attempt * 30)
            response = requests.get(url, timeout=timeout)

            # Check for HTTP errors
            if response.status_code == 404:
                return f"❌ Page not found (404): {url}"
            elif response.status_code == 504:
                # Gateway timeout - retry with exponential backoff
                last_error = f"Gateway timeout (504)"
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt) if progressive_delay else retry_delay * (attempt + 1)
                    print(f"   ⚠️  {last_error}, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                    continue
                else:
                    return f"❌ Gateway timeout (504) after {max_retries} attempts: {url}"
            elif response.status_code != 200:
                return f"❌ HTTP Error {response.status_code}: {url}"

            content = response.text

            # Cache successful responses
            _cache.set(url, content)

            return content

        except requests.exceptions.Timeout:
            last_error = "Request timeout"
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt) if progressive_delay else retry_delay * (attempt + 1)
                print(f"   ⚠️  {last_error}, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
                continue
            else:
                return f"❌ Timeout error after {max_retries} attempts: {url}"
        except requests.exceptions.ConnectionError:
            last_error = "Connection error"
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt) if progressive_delay else retry_delay * (attempt + 1)
                print(f"   ⚠️  {last_error}, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
                continue
            else:
                return f"❌ Connection error after {max_retries} attempts: {url}"
        except requests.exceptions.RequestException as e:
            return f"❌ Request error: {e}"
        except Exception as e:
            return f"❌ Unexpected error: {e}"

    return f"❌ Failed after {max_retries} attempts: {last_error}"


def fetch_search_results(variety_name: str) -> str:
    """Fetch search results from VIVC."""
    encoded_name = urllib.parse.quote_plus(variety_name)
    search_url = f"https://www.vivc.de/index.php?r=cultivarname%2Findex&CultivarnameSearch%5Bcultivarnames%5D=&CultivarnameSearch%5Bcultivarnames%5D=cultivarn&CultivarnameSearch%5Btext%5D={encoded_name}"
    return fetch_url(search_url)


def fetch_passport_page(vivc_number: str) -> str:
    """Fetch passport page from VIVC."""
    passport_url = f"https://www.vivc.de/index.php?r=passport%2Fview&id={vivc_number}"
    return fetch_url(passport_url)


def extract_search_results(html_content: str) -> List[VarietySearchResult]:
    """Extract structured search results from VIVC search page."""
    results = []
    seen_vivc = set()
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the results table
        table = soup.find('table')
        if not table:
            return results
        
        # Find all rows with data
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            
            # Skip header rows or rows without enough columns
            if len(cells) < 6:
                continue
            
            # Extract text from each cell
            cell_texts = [cell.get_text().strip() for cell in cells]
            
            # Look for VIVC number link in the row
            vivc_link = row.find('a', href=lambda x: x and 'passport' in x and 'view' in x)
            if not vivc_link:
                continue
                
            href = vivc_link.get('href', '')
            vivc_match = re.search(r'id=(\d+)', href)
            if not vivc_match:
                continue
                
            vivc_number = vivc_match.group(1)
            
            # Skip duplicates
            if vivc_number in seen_vivc:
                continue
            seen_vivc.add(vivc_number)
            
            # Map columns based on VIVC table structure:
            # 0: Cultivar name
            # 1: Prime name  
            # 2: Variety number VIVC (contains the link)
            # 3: Species
            # 4: Color of berry skin
            # 5: Country or region of origin
            
            result = VarietySearchResult(
                cultivar_name=cell_texts[0] if len(cell_texts) > 0 else None,
                prime_name=cell_texts[1] if len(cell_texts) > 1 else None,
                vivc_number=vivc_number,
                species=cell_texts[3] if len(cell_texts) > 3 else None,
                berry_skin_color=cell_texts[4] if len(cell_texts) > 4 else None,
                country_of_origin=cell_texts[5] if len(cell_texts) > 5 else None,
                passport_url=f"https://www.vivc.de/{href}" if not href.startswith('http') else href
            )
            
            results.append(result)
    
    except Exception as e:
        pass
    
    return results


def parse_passport_html(html_content: str) -> PassportData:
    """Parse passport HTML directly and return structured data."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract data from the main passport table
        table_data = {}
        
        # Find passport data table
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    table_data[key] = value
        
        # Extract main grape information
        grape_name = table_data.get('Prime name')
        grape_vivc = table_data.get('Variety number VIVC')
        main_grape = GrapeId(name=grape_name, vivc_number=grape_vivc)
        
        # Extract parent information
        parent1_grape = None
        parent2_grape = None
        
        parent1_name = table_data.get('Prime name of parent 1')
        parent2_name = table_data.get('Prime name of parent 2')
        
        # Find parent VIVC numbers from links
        parent_links = soup.find_all('a', href=re.compile(r'passport.*view.*id=\d+'))
        
        if parent1_name:
            parent1_vivc = None
            for link in parent_links:
                if parent1_name.upper() in link.get_text().upper():
                    href = link.get('href', '')
                    vivc_match = re.search(r'id=(\d+)', href)
                    if vivc_match:
                        parent1_vivc = vivc_match.group(1)
                        break
            parent1_grape = GrapeId(name=parent1_name, vivc_number=parent1_vivc)
        
        if parent2_name:
            parent2_vivc = None
            for link in parent_links:
                if parent2_name.upper() in link.get_text().upper():
                    href = link.get('href', '')
                    vivc_match = re.search(r'id=(\d+)', href)
                    if vivc_match:
                        parent2_vivc = vivc_match.group(1)
                        break
            parent2_grape = GrapeId(name=parent2_name, vivc_number=parent2_vivc)
        
        # Extract synonyms from synonyms table
        synonyms = []
        for table in soup.find_all('table'):
            table_text = table.get_text()
            if 'Synonyms:' in table_text:
                synonym_links = table.find_all('a')
                for link in synonym_links:
                    href = link.get('href', '')
                    if 'sname' in href or 'synonym' in href.lower():
                        synonym_name = link.get_text().strip()
                        if synonym_name and synonym_name not in synonyms:
                            synonyms.append(synonym_name)
        
        # Create and return PassportData object
        return PassportData(
            grape=main_grape,
            berry_skin_color=table_data.get('Color of berry skin'),
            country_of_origin=table_data.get('Country or region of origin of the variety'),
            species=table_data.get('Species'),
            parent1=parent1_grape,
            parent2=parent2_grape,
            sex_of_flower=table_data.get('Sex of flowers'),
            number_of_photos=table_data.get('Photos of the cultivar'),
            year_of_crossing=table_data.get('Year of crossing'),
            synonyms=synonyms if synonyms else None
        )
        
    except Exception as e:
        # Return empty data on parsing error
        return PassportData(grape=GrapeId())


# Public API functions

def search_cultivar(variety_name: str) -> List[VarietySearchResult]:
    """Search for a cultivar name and return results.
    
    Args:
        variety_name: Name of the grape variety to search for
        
    Returns:
        List of VarietySearchResult objects
        
    Raises:
        ValueError: If search fails or no results found
    """
    html_content = fetch_search_results(variety_name)
    
    if html_content.startswith("❌"):
        raise ValueError(html_content)
    
    results = extract_search_results(html_content)
    
    if not results:
        raise ValueError(f"No results found for '{variety_name}'")
    
    return results


def get_passport_data(vivc_number: str) -> PassportData:
    """Get passport data for a VIVC number.

    Args:
        vivc_number: VIVC catalog number

    Returns:
        PassportData object with structured information

    Raises:
        ValueError: If unable to fetch or parse data
    """
    html_content = fetch_passport_page(vivc_number)

    if html_content.startswith("❌"):
        raise ValueError(html_content)

    return parse_passport_html(html_content)


def extract_photo_credits(vivc_number: str, photo_id: str, delay: float = 3.0) -> Optional[PhotoCredit]:
    """Extract photo credits from VIVC foto2 modal.

    When you click a photo on VIVC, it calls showFoto2(photo_id, vivc_id) which loads
    a modal via AJAX from: index.php?r=datasheet/foto2&id={photo_id}&kennnr={vivc_id}

    This modal contains the photo credit text like:
    "Please note: This photo can be reproduced. Please quote the source as indicated below:
     Ursula Brühl, Julius Kühn-Institut (JKI)..."

    OR for external photos:
    "Note: For the reproduction of external photos, please contact the indicated source
     for permission: Tom Plocher, Plocher-Vines LLC..."

    Args:
        vivc_number: VIVC catalog number (kennnr parameter)
        photo_id: Photo ID from the onclick handler
        delay: Delay before making request (default: 3.0)

    Returns:
        PhotoCredit object with note and credit fields, or None if not found or error occurred
    """
    foto2_url = f"https://www.vivc.de/index.php?r=datasheet/foto2&id={photo_id}&kennnr={vivc_number}"

    try:
        html_content = fetch_url(foto2_url, delay=delay)

        if html_content.startswith("❌"):
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()

        # Look for credit text patterns
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        note_line = None
        credit_line = None

        for i, line in enumerate(lines):
            # Look for the "Please note" or "Note:" usage text
            if ('reproduced' in line.lower() or 'reproduction' in line.lower()) and \
               ('quote' in line.lower() or 'contact' in line.lower() or 'permission' in line.lower()):
                # Found the note line
                note_line = line

                # The credit source is usually 2-4 lines after the note
                for j in range(i + 1, min(len(lines), i + 6)):
                    potential_credit = lines[j]
                    # Skip empty lines and generic text
                    if not potential_credit or potential_credit in ['Please note:', 'Note:']:
                        continue
                    # Look for patterns like name/institution with address
                    if any(indicator in potential_credit for indicator in [
                        'Julius Kühn', 'JKI', 'Brühl', 'Geilweilerhof',  # JKI credits
                        ',', 'LLC', 'USA', 'Institute', 'University'      # General institution indicators
                    ]):
                        credit_line = potential_credit
                        break

                if note_line and credit_line:
                    return PhotoCredit(note=note_line, credit=credit_line)

        # If we didn't find it with the above logic, try a simpler approach
        # Look for text that looks like a source attribution
        text_lower = text.lower()
        if 'external photo' in text_lower or 'reproduction of external' in text_lower:
            # This is an external photo - try to extract both parts
            for i, line in enumerate(lines):
                if 'external' in line.lower() and 'permission' in line.lower():
                    note_line = line
                    # Next substantial line should be the source
                    for j in range(i + 1, min(len(lines), i + 6)):
                        if lines[j] and ',' in lines[j] and len(lines[j]) > 20:
                            credit_line = lines[j]
                            break
                    if note_line and credit_line:
                        return PhotoCredit(note=note_line, credit=credit_line)

        # No credits found
        return None

    except Exception as e:
        return None


def extract_photo_ids_from_photoview(vivc_number: str) -> List[tuple[str, str, str]]:
    """Extract photo IDs from photoviewresult page.

    Parses the photoviewresult page to find all photo IDs from onclick handlers
    like: onclick="showFoto2(12774,'17638',1)"

    Args:
        vivc_number: VIVC catalog number

    Returns:
        List of (photo_id, photo_type, photo_url) tuples
    """
    photoview_url = f"https://www.vivc.de/index.php?r=passport/photoviewresult&id={vivc_number}"

    try:
        html_content = fetch_url(photoview_url)

        if html_content.startswith("❌"):
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        photos = []

        # Find all img tags with onclick handlers
        img_tags = soup.find_all('img', onclick=True)

        for img in img_tags:
            onclick = img.get('onclick', '')
            if 'showFoto2' in onclick:
                # Extract photo ID from showFoto2(12774,'17638',1)
                match = re.search(r'showFoto2\((\d+),', onclick)
                if match:
                    photo_id = match.group(1)
                    photo_url = img.get('src', '')

                    # Try to get photo type from surrounding context
                    photo_type = "Unknown"
                    panel = img.find_parent('div', class_='panel-body')
                    if panel:
                        panel_parent = panel.find_parent('div', class_='panel2')
                        if panel_parent:
                            title_elem = panel_parent.find('h4', class_='panel-title')
                            if title_elem:
                                title_text = title_elem.get_text()
                                if 'Category:' in title_text:
                                    photo_type = title_text.split('Category:')[-1].strip()

                    photos.append((photo_id, photo_type, photo_url))

        return photos

    except Exception as e:
        return []


def get_photo_credit_for_variety(vivc_number: str, delay: float = 3.0) -> Optional[PhotoCredit]:
    """Get photo credit for the first available photo of a variety.

    This is a convenience function that:
    1. Fetches the photoviewresult page
    2. Extracts the first photo ID
    3. Fetches the foto2 modal for that photo
    4. Extracts the credit text

    Args:
        vivc_number: VIVC catalog number
        delay: Delay before making requests (default: 3.0)

    Returns:
        PhotoCredit object with note and credit fields, or None if not found
    """
    photos = extract_photo_ids_from_photoview(vivc_number)

    if not photos:
        return None

    # Get credits for the first photo
    photo_id, photo_type, photo_url = photos[0]
    return extract_photo_credits(vivc_number, photo_id, delay=delay)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="VIVC Client - Search and fetch passport data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for varieties
  python src/includes/vivc_client.py search "seyval blanc"
  
  # Get passport data  
  python src/includes/vivc_client.py passport 15904
  
  # Debug modes
  python src/includes/vivc_client.py search "frontenac" --dump-html
  python src/includes/vivc_client.py passport 15904 --debug-markdown
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for grape varieties')
    search_parser.add_argument('variety_name', help='Name of the grape variety to search for')
    search_parser.add_argument('--dump-html', '-d', action='store_true', help='Dump raw HTML instead of parsing results')
    
    # Passport command
    passport_parser = subparsers.add_parser('passport', help='Get passport data for VIVC number')
    passport_parser.add_argument('vivc_number', help='VIVC catalog number to fetch')
    passport_parser.add_argument('--debug-markdown', '-d', action='store_true', help='Output raw markdown for debugging')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'search':
            if args.dump_html:
                # Debug mode: dump raw HTML
                html_content = fetch_search_results(args.variety_name)
                if html_content.startswith("❌"):
                    print(html_content)
                    sys.exit(1)
                
                search_url = f"https://www.vivc.de/index.php?r=cultivarname%2Findex&CultivarnameSearch%5Bcultivarnames%5D=&CultivarnameSearch%5Bcultivarnames%5D=cultivarn&CultivarnameSearch%5Btext%5D={urllib.parse.quote_plus(args.variety_name)}"
                print(f"Search URL: {search_url}")
                print("\n" + "=" * 80)
                print("RAW HTML CONTENT:")
                print("=" * 80)
                print(html_content)
            else:
                # Normal search
                results = search_cultivar(args.variety_name)
                results_dict = [result.to_dict() for result in results]
                print(json.dumps(results_dict, indent=2))
        
        elif args.command == 'passport':
            if not args.vivc_number.isdigit():
                print("❌ VIVC number must be numeric")
                sys.exit(1)
            
            if args.debug_markdown:
                # Debug mode
                html_content = fetch_passport_page(args.vivc_number)
                if html_content.startswith("❌"):
                    print(html_content)
                    sys.exit(1)
                
                print("DEBUG: HTML fetched successfully, length:", len(html_content))
                print("=" * 60)
                print("Parsing HTML directly now...")
            else:
                # Normal passport fetch
                passport_data = get_passport_data(args.vivc_number)
                print(passport_data.to_json())
    
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()