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


def fetch_url(url: str) -> str:
    """Fetch URL with caching and throttling.
    
    Args:
        url: URL to fetch
        
    Returns:
        Raw HTML content or error message
    """
    # Check cache first
    cached_content = _cache.get(url)
    if cached_content:
        return cached_content
    
    # Throttle: wait 1 second before making any HTTP request
    time.sleep(1)
    
    try:
        response = requests.get(url, timeout=30)
        
        # Check for HTTP errors
        if response.status_code == 404:
            return f"❌ Page not found (404): {url}"
        elif response.status_code != 200:
            return f"❌ HTTP Error {response.status_code}: {url}"
        
        content = response.text
        
        # Cache successful responses
        _cache.set(url, content)
        
        return content
        
    except requests.exceptions.Timeout:
        return f"❌ Timeout error: {url}"
    except requests.exceptions.ConnectionError:
        return f"❌ Connection error: {url}"
    except requests.exceptions.RequestException as e:
        return f"❌ Request error: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


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