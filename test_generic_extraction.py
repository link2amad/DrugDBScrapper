#!/usr/bin/env python3
"""
Test script to verify generic name extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.dawaai_scraper import DawaaiScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_generic_extraction():
    """Test generic name extraction"""
    
    # Initialize scraper
    scraper = DawaaiScraper()
    
    # Test URLs that should have generic information
    test_urls = [
        "https://dawaai.pk/medicine/arnil-1-34352.html",
        "https://dawaai.pk/medicine/artifen-34359.html",
        "https://dawaai.pk/medicine/advacort-ointment-34383.html"
    ]
    
    for url in test_urls:
        print(f"\n=== Testing URL: {url} ===")
        
        try:
            # First get listing data for this medicine
            # We need to simulate the listing data that would normally come from the letter page
            listing_data = {
                'brand_name': 'Test Brand',  # This would normally come from listing page
                'pack_size': 'Test Pack Size',  # This would normally come from listing page
                'price': 100.0,  # This would normally come from listing page
                'original_price': 120.0  # This would normally come from listing page
            }
            
            # Extract medicine data with listing data
            detail_data = scraper._extract_medicine_data(url, listing_data)
            
            if detail_data:
                print(f"Complete Name: {detail_data.get('complete_name')}")
                print(f"Brand Name: {detail_data.get('brand_name')}")
                print(f"Generic Name: {detail_data.get('generic_name')}")
                print(f"Pack Size: {detail_data.get('pack_size')}")
                print(f"Listing Price: {detail_data.get('listing_price')}")
                print(f"Detail Price: {detail_data.get('detail_price')}")
            else:
                print("Could not extract data")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_generic_extraction() 