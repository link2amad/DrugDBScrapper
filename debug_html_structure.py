#!/usr/bin/env python3
"""
Debug script to understand HTML structure and find correct containers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.dawaai_scraper import DawaaiScraper
import logging
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_html_structure():
    """Debug HTML structure to find correct containers"""
    
    # Initialize scraper
    scraper = DawaaiScraper()
    
    # Get the page content
    letter_url = "https://dawaai.pk/all-medicines/a"
    response = scraper._get_page_with_retry(letter_url)
    
    if not response:
        print("Could not fetch page")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all medicine links
    medicine_links = soup.find_all('a', href=True)
    medicine_links = [link for link in medicine_links if '/medicine/' in link.get('href')]
    
    print(f"Found {len(medicine_links)} medicine links")
    
    # Analyze first few links
    for i, link in enumerate(medicine_links[:3]):
        print(f"\n=== Link {i+1} ===")
        print(f"URL: {link.get('href')}")
        print(f"Link text: {link.get_text(strip=True)}")
        
        # Try different container strategies
        print("\n🔍 Container Analysis:")
        
        # Strategy 1: Direct parent
        parent = link.find_parent()
        if parent:
            print(f"Direct parent: {parent.name} (class: {parent.get('class', 'None')})")
            print(f"Parent text: {parent.get_text(strip=True)[:100]}...")
        
        # Strategy 2: Look for parent with specific classes
        for class_name in ['product', 'medicine', 'card', 'item']:
            container = link.find_parent(class_=lambda x: x and class_name in x.lower())
            if container:
                print(f"Parent with '{class_name}': {container.name} (class: {container.get('class', 'None')})")
                print(f"Container text: {container.get_text(strip=True)[:100]}...")
                break
        
        # Strategy 3: Look for any parent containing price info
        for parent in link.parents:
            if parent and parent.get_text():
                parent_text = parent.get_text(strip=True)
                if 'Rs' in parent_text:
                    print(f"Parent with 'Rs': {parent.name} (class: {parent.get('class', 'None')})")
                    print(f"Text: {parent_text[:200]}...")
                    break
        
        # Strategy 4: Look for siblings that might contain price info
        siblings = link.find_next_siblings()
        for sibling in siblings[:3]:
            if sibling and sibling.get_text():
                sibling_text = sibling.get_text(strip=True)
                if 'Rs' in sibling_text or 'Pack Size' in sibling_text:
                    print(f"Sibling with price/pack info: {sibling.name} (class: {sibling.get('class', 'None')})")
                    print(f"Text: {sibling_text[:100]}...")
        
        print("-" * 50)

if __name__ == "__main__":
    debug_html_structure() 