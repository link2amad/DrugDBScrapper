#!/usr/bin/env python3
"""
Debug script to investigate container data extraction issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.dawaai_scraper import DawaaiScraper
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_container_extraction():
    """Debug container data extraction"""
    
    # Initialize scraper
    scraper = DawaaiScraper()
    
    # Get medicine links for letter 'a'
    letter_url = "https://dawaai.pk/all-medicines/a"
    medicine_data_list = scraper._extract_medicine_links(letter_url)
    
    print(f"Found {len(medicine_data_list)} medicine links")
    
    # Test first few medicines
    for i, medicine_data in enumerate(medicine_data_list[:3]):
        print(f"\n=== Medicine {i+1} ===")
        print(f"URL: {medicine_data['url']}")
        print(f"Brand Name: {medicine_data.get('brand_name')}")
        print(f"Pack Size: {medicine_data.get('pack_size')}")
        print(f"Price: {medicine_data.get('price')}")
        print(f"Original Price: {medicine_data.get('original_price')}")

if __name__ == "__main__":
    debug_container_extraction() 