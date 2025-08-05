#!/usr/bin/env python3
"""
Pakistan Medical Industry Drug Database Scraper
Scrapes medicine data from dawaai.pk and stores in MSSQL database
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from scraper import DawaaiScraper, DatabaseHandler
from config import DatabaseConfig

def setup_logging(log_level=logging.INFO):
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'logs/scraper_{timestamp}.log'
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def test_database_connection():
    """Test database connection"""
    logger = logging.getLogger(__name__)
    logger.info("Testing database connection...")
    
    try:
        db_handler = DatabaseHandler()
        db_handler.create_table_if_not_exists()
        db_handler.add_new_columns_if_not_exist()  # Add new columns for existing databases
        logger.info("Database connection successful!")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.error("Please check your database configuration in .env file")
        return False

def scrape_single_letter(letter):
    """Scrape medicines for a single letter"""
    logger = logging.getLogger(__name__)
    logger.info(f"Starting to scrape letter: {letter}")
    
    try:
        scraper = DawaaiScraper()
        scraper.scrape_letter(letter)
        logger.info(f"Completed scraping letter: {letter}")
        return True
    except Exception as e:
        logger.error(f"Error scraping letter {letter}: {e}")
        return False

def scrape_all_letters():
    """Scrape medicines for all letters A-Z"""
    logger = logging.getLogger(__name__)
    logger.info("Starting to scrape all letters A-Z")
    
    try:
        scraper = DawaaiScraper()
        scraper.scrape_all_letters()
        logger.info("Completed scraping all letters")
        return True
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return False

def show_database_stats():
    """Show database statistics"""
    logger = logging.getLogger(__name__)
    logger.info("Fetching database statistics...")
    
    try:
        db_handler = DatabaseHandler()
        stats = db_handler.get_statistics()
        
        if stats:
            logger.info("=" * 40)
            logger.info("DATABASE STATISTICS")
            logger.info("=" * 40)
            logger.info(f"Total medicines: {stats['total_medicines']}")
            logger.info(f"Medicines with images: {stats['medicines_with_images']}")
            logger.info(f"Medicines with generic names: {stats['medicines_with_generic_names']}")
            logger.info(f"Medicines with listing prices: {stats['medicines_with_listing_prices']}")
            logger.info(f"Medicines with detail prices: {stats['medicines_with_detail_prices']}")
            logger.info(f"First record: {stats['first_record']}")
            logger.info(f"Last record: {stats['last_record']}")
            logger.info("=" * 40)
        else:
            logger.warning("Could not retrieve database statistics")
            
    except Exception as e:
        logger.error(f"Error getting database statistics: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Pakistan Medical Industry Drug Database Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --test-db                    # Test database connection
  python main.py --scrape-letter a            # Scrape medicines starting with 'a'
  python main.py --scrape-all                 # Scrape all letters A-Z
  python main.py --stats                      # Show database statistics
  python main.py --scrape-all --verbose       # Scrape all with verbose logging
        """
    )
    
    parser.add_argument('--test-db', action='store_true',
                       help='Test database connection')
    parser.add_argument('--scrape-letter', type=str, metavar='LETTER',
                       help='Scrape medicines for specific letter (a-z)')
    parser.add_argument('--scrape-all', action='store_true',
                       help='Scrape medicines for all letters A-Z')
    parser.add_argument('--stats', action='store_true',
                       help='Show database statistics')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    logger.info("=" * 60)
    logger.info("PAKISTAN MEDICAL INDUSTRY DRUG DATABASE SCRAPER")
    logger.info("=" * 60)
    logger.info(f"Started at: {datetime.now()}")
    
    # Check if any action is specified
    if not any([args.test_db, args.scrape_letter, args.scrape_all, args.stats]):
        logger.error("No action specified. Use --help for usage information.")
        return 1
    
    # Test database connection
    if args.test_db:
        if not test_database_connection():
            return 1
    
    # Show database statistics
    if args.stats:
        show_database_stats()
    
    # Scrape specific letter
    if args.scrape_letter:
        letter = args.scrape_letter.lower()
        if not letter.isalpha() or len(letter) != 1:
            logger.error("Letter must be a single alphabetic character (a-z)")
            return 1
        
        if not scrape_single_letter(letter):
            return 1
    
    # Scrape all letters
    if args.scrape_all:
        if not scrape_all_letters():
            return 1
    
    logger.info("=" * 60)
    logger.info("SCRAPER COMPLETED SUCCESSFULLY")
    logger.info(f"Finished at: {datetime.now()}")
    logger.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 