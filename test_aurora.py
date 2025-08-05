#!/usr/bin/env python3
"""
Test script to check if Aurora 20mg variant is found in the medicine links
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.dawaai_scraper import DawaaiScraper
from scraper.database_handler import DatabaseHandler
from config.database_config import DatabaseConfig
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_aurora_variants():
    """Test if both Aurora variants are found"""
    
    # Initialize scraper
    scraper = DawaaiScraper()
    
    # Get medicine links for letter 'a'
    letter_url = "https://dawaai.pk/all-medicines/a"
    medicine_data_list = scraper._extract_medicine_links(letter_url)
    
    print(f"Found {len(medicine_data_list)} medicine links")
    
    # Look for Aurora variants
    aurora_variants = []
    for medicine_data in medicine_data_list:
        url = medicine_data['url']
        if 'aurora' in url.lower():
            aurora_variants.append(url)
    
    print(f"\nFound {len(aurora_variants)} Aurora variants:")
    for url in aurora_variants:
        print(f"  - {url}")
    
    # Check specific variants
    aurora_10mg_found = any('aurora-tab-5mg-10s-36775' in url for url in aurora_variants)
    aurora_20mg_found = any('aurora-44165' in url for url in aurora_variants)
    
    print(f"\nAurora 10mg (aurora-tab-5mg-10s-36775): {'✅ Found' if aurora_10mg_found else '❌ Not found'}")
    print(f"Aurora 20mg (aurora-44165): {'✅ Found' if aurora_20mg_found else '❌ Not found'}")
    
    # Check database for existing Aurora records
    db_handler = DatabaseHandler()
    
    # Check if Aurora 10mg exists in database
    aurora_10mg_exists = db_handler.medicine_exists('aurora-tab-5mg-10s-36775')
    aurora_20mg_exists = db_handler.medicine_exists('aurora-44165')
    
    print(f"\nDatabase status:")
    print(f"Aurora 10mg in database: {'✅ Yes' if aurora_10mg_exists else '❌ No'}")
    print(f"Aurora 20mg in database: {'✅ Yes' if aurora_20mg_exists else '❌ No'}")

if __name__ == "__main__":
    test_aurora_variants() 