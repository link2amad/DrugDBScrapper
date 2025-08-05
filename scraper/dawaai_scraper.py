import requests
import logging
import time
import random
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .database_handler import DatabaseHandler
from .image_downloader import ImageDownloader

class DawaaiScraper:
    def __init__(self, base_url="https://dawaai.pk"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.db_handler = DatabaseHandler()
        self.image_downloader = ImageDownloader()
        
        # Initialize session with anti-blocking measures
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # Set up rotating user agents and headers
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        })
        
        # Rate limiting settings
        self.min_delay = 2
        self.max_delay = 5
        self.max_retries = 3
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'new_medicines': 0,
            'updated_medicines': 0,
            'failed_requests': 0,
            'images_downloaded': 0
        }
    
    def _get_page_with_retry(self, url, max_retries=None):
        """Get page content with retry logic and anti-blocking measures"""
        if max_retries is None:
            max_retries = self.max_retries
            
        for attempt in range(max_retries):
            try:
                # Rotate user agent
                self.session.headers['User-Agent'] = self.ua.random
                
                # Add random delay
                time.sleep(random.uniform(self.min_delay, self.max_delay))
                
                # Make request
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                self.stats['failed_requests'] += 1
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"All attempts failed for {url}")
                    return None
        
        return None
    
    def _extract_external_id(self, url):
        """Extract external ID from medicine URL"""
        try:
            # Extract ID from URL like: /medicine/arnil-1-34352.html
            match = re.search(r'/medicine/([^/]+)\.html', url)
            if match:
                return match.group(1)
            
            # Fallback: use the full URL as external ID
            return url.replace(self.base_url, '').replace('/', '_')
            
        except Exception as e:
            self.logger.error(f"Error extracting external ID from {url}: {e}")
            return url
    
    def _extract_medicine_links(self, letter_url):
        """Extract all medicine links and basic info from a letter page"""
        medicine_data = []
        
        try:
            response = self._get_page_with_retry(letter_url)
            if not response:
                return medicine_data
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for medicine cards/containers
            medicine_containers = soup.select('.product-card, .medicine-card, .item, [class*="card"], [class*="product"]')
            
            if not medicine_containers:
                # Fallback: look for any container with medicine links
                medicine_containers = soup.find_all('div', class_=lambda x: x and any(keyword in x.lower() for keyword in ['product', 'medicine', 'item']))
            
            for container in medicine_containers:
                try:
                    # Extract medicine link
                    link_element = container.select_one('a[href*="/medicine/"]')
                    if not link_element:
                        continue
                    
                    href = link_element.get('href')
                    if not href or '/medicine/' not in href:
                        continue
                    
                    full_url = urljoin(self.base_url, href)
                    
                    # Extract basic info from listing page
                    listing_data = self._extract_listing_page_data(container)
                    
                    medicine_data.append({
                        'url': full_url,
                        'brand_name': listing_data.get('brand_name'),
                        'pack_size': listing_data.get('pack_size'),
                        'price': listing_data.get('price'),
                        'original_price': listing_data.get('original_price')
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Error processing medicine container: {e}")
                    continue
            
            self.logger.info(f"Found {len(medicine_data)} medicine links on {letter_url}")
            return medicine_data
            
        except Exception as e:
            self.logger.error(f"Error extracting medicine links from {letter_url}: {e}")
            return medicine_data
    
    def _extract_listing_page_data(self, container):
        """Extract basic data from listing page container"""
        try:
            data = {}
            
            # Get all text content from the container
            container_text = container.get_text(strip=True)
            self.logger.debug(f"Container text: {container_text}")
            
            # Extract brand name - look for text that appears before "Pack Size"
            brand_name = self._extract_brand_name_from_text(container_text)
            if brand_name:
                data['brand_name'] = brand_name
            
            # Extract pack size - look for "Pack Size:" pattern
            pack_size = self._extract_pack_size_from_text(container_text)
            if pack_size:
                data['pack_size'] = pack_size
            
            # Extract price information
            price, original_price = self._extract_price_from_container(container)
            if price:
                data['price'] = price
            if original_price:
                data['original_price'] = original_price
            
            self.logger.debug(f"Extracted data: {data}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error extracting listing page data: {e}")
            return {}
    
    def _extract_brand_name_from_text(self, text):
        """Extract brand name from text content"""
        try:
            # Clean the text first - remove promotional content
            cleaned_text = self._clean_promotional_text(text)
            
            # Look for patterns like "BrandName" followed by "Pack Size"
            # Common patterns: "AxicamMass-PH Health", "AdronilSearle"
            
            # Pattern 1: Look for text before "Pack Size"
            pack_size_match = re.search(r'Pack\s+Size', cleaned_text, re.IGNORECASE)
            if pack_size_match:
                before_pack_size = cleaned_text[:pack_size_match.start()].strip()
                if before_pack_size:
                    # Clean up the brand name
                    brand = self._clean_brand_name(before_pack_size)
                    if brand:
                        return brand
            
            # Pattern 2: Look for common brand name patterns
            brand_patterns = [
                r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Capitalized words
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Pack',  # Brand followed by "Pack"
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Rs',  # Brand followed by "Rs"
            ]
            
            for pattern in brand_patterns:
                match = re.search(pattern, cleaned_text)
                if match:
                    brand = match.group(1).strip()
                    brand = self._clean_brand_name(brand)
                    if brand and len(brand) > 2 and len(brand) < 50:  # Reasonable brand name length
                        return brand
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting brand name from text: {e}")
            return None
    
    def _clean_promotional_text(self, text):
        """Remove promotional content from text"""
        try:
            # Remove promotional text patterns
            promotional_patterns = [
                r'10%\s*Off',  # "10% Off"
                r'\d+%\s*Off',  # Any percentage off
                r'Off\s*',      # "Off" followed by space
                r'Discount',    # "Discount"
                r'Sale',        # "Sale"
                r'Promotion',   # "Promotion"
                r'Special\s+Offer',  # "Special Offer"
                r'Limited\s+Time',   # "Limited Time"
                r'Free\s+Shipping',  # "Free Shipping"
                r'Buy\s+One\s+Get\s+One',  # "Buy One Get One"
                r'BOGO',        # "BOGO"
                r'New',         # "New" (when standalone)
                r'Best\s+Seller',  # "Best Seller"
                r'Top\s+Rated',     # "Top Rated"
                r'Featured',        # "Featured"
            ]
            
            cleaned_text = text
            for pattern in promotional_patterns:
                cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
            
            # Remove extra whitespace
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Error cleaning promotional text: {e}")
            return text
    
    def _clean_brand_name(self, brand_text):
        """Clean and validate brand name"""
        try:
            if not brand_text:
                return None
            
            # Remove common suffixes and prefixes
            suffixes_to_remove = [
                r'\s+(Health|Limited|Pharma|Laboratories?|Ltd|Inc|Corp|Company|International|Industries?|Group|Enterprises?)$',
                r'\s+(Pakistan|Pvt|Private|Public|Co|Corporation)$',
                r'\s+(Pharmaceuticals?|Medicines?|Drugs?|Products?)$',
                r'\s+(Manufacturing|Trading|Marketing|Distribution)$',
            ]
            
            cleaned_brand = brand_text
            for pattern in suffixes_to_remove:
                cleaned_brand = re.sub(pattern, '', cleaned_brand, flags=re.IGNORECASE)
            
            # Remove extra whitespace and clean up
            cleaned_brand = re.sub(r'\s+', ' ', cleaned_brand).strip()
            
            # Validate brand name
            if cleaned_brand and len(cleaned_brand) > 2 and len(cleaned_brand) < 50:
                # Check if it contains reasonable brand name characters
                if re.match(r'^[A-Za-z\s\-\.&]+$', cleaned_brand):
                    return cleaned_brand
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error cleaning brand name: {e}")
            return None
    
    def _extract_pack_size_from_text(self, text):
        """Extract pack size from text content"""
        try:
            # Look for "Pack Size:" pattern
            pack_size_patterns = [
                r'Pack\s+Size:\s*([^Rs]+)',  # "Pack Size: 1x20's"
                r'Pack\s+Size:\s*([^,]+)',   # "Pack Size: 1 Ampx3ml"
                r'(\d+x\d+\'s)',             # "2x10's"
                r'(\d+\s*[A-Za-z]+)',        # "1 Ampx3ml", "10 tablets"
            ]
            
            for pattern in pack_size_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    pack_size = match.group(1).strip()
                    if pack_size and len(pack_size) > 0:
                        return pack_size
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting pack size from text: {e}")
            return None
    
    def _extract_price_from_container(self, container):
        """Extract price and original price from container"""
        try:
            price = None
            original_price = None
            
            # Get all text content from the container
            container_text = container.get_text(strip=True)
            
            # Look for price patterns in the text
            # Pattern: "Rs 226Rs 252" or "Rs 2,008Rs 2,231"
            price_pattern = r'Rs\s*(\d+(?:,\d+)*)Rs\s*(\d+(?:,\d+)*)'
            price_match = re.search(price_pattern, container_text)
            
            if price_match:
                try:
                    # First price is usually the current price
                    price_str = price_match.group(1).replace(',', '')
                    price = float(price_str)
                    
                    # Second price is usually the original price
                    original_str = price_match.group(2).replace(',', '')
                    original_price = float(original_str)
                    
                    return price, original_price
                except ValueError:
                    pass
            
            # Fallback: Look for individual price elements
            price_selectors = [
                '.price',
                '.current-price',
                '.discounted-price',
                '.sale-price',
                'span[class*="price"]',
                'div[class*="price"]'
            ]
            
            original_price_selectors = [
                '.original-price',
                '.old-price',
                '.strike-price',
                'span[class*="original"]',
                'div[class*="original"]'
            ]
            
            # Extract current price
            for selector in price_selectors:
                element = container.select_one(selector)
                if element:
                    price_text = element.get_text(strip=True)
                    price_match = re.search(r'Rs\s*(\d+(?:,\d+)*)', price_text)
                    if price_match:
                        price_str = price_match.group(1).replace(',', '')
                        try:
                            price = float(price_str)
                            break
                        except ValueError:
                            continue
            
            # Extract original price
            for selector in original_price_selectors:
                element = container.select_one(selector)
                if element:
                    original_text = element.get_text(strip=True)
                    original_match = re.search(r'Rs\s*(\d+(?:,\d+)*)', original_text)
                    if original_match:
                        original_str = original_match.group(1).replace(',', '')
                        try:
                            original_price = float(original_str)
                            break
                        except ValueError:
                            continue
            
            return price, original_price
            
        except Exception as e:
            self.logger.error(f"Error extracting price from container: {e}")
            return None, None
    
    def _extract_medicine_data(self, medicine_url, listing_data=None):
        """Extract detailed medicine data from individual medicine page"""
        try:
            response = self._get_page_with_retry(medicine_url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract complete name (keep original logic)
            complete_name = self._extract_complete_name(soup)
            
            # Use listing data for brand name, pack size, and listing prices
            brand_name = listing_data.get('brand_name') if listing_data else None
            pack_size = listing_data.get('pack_size') if listing_data else None
            listing_price = listing_data.get('price') if listing_data else None
            listing_original_price = listing_data.get('original_price') if listing_data else None
            
            # Extract detail page prices
            detail_price, detail_original_price = self._extract_detail_page_prices(soup)
            
            # Extract generic name (enhanced)
            generic_name = self._extract_generic_name(soup)
            
            # Extract generic reference link
            generic_ref_link = self._extract_generic_ref_link(soup)
            
            # Extract image URL
            image_url = self.image_downloader.extract_image_url(soup, self.base_url)
            
            return {
                'complete_name': complete_name,
                'brand_name': brand_name,
                'generic_name': generic_name,
                'pack_size': pack_size,
                'listing_price': listing_price,
                'listing_original_price': listing_original_price,
                'detail_price': detail_price,
                'detail_original_price': detail_original_price,
                'generic_ref_link': generic_ref_link,
                'drug_external_link': medicine_url,
                'image_url': image_url
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting medicine data from {medicine_url}: {e}")
            return None
    
    def _extract_detail_page_prices(self, soup):
        """Extract price and original price from detail page"""
        try:
            price = None
            original_price = None
            
            # Look for price elements on detail page
            price_selectors = [
                '.price',
                '.current-price',
                '.discounted-price',
                '.sale-price',
                '.product-price',
                '.medicine-price',
                'span[class*="price"]',
                'div[class*="price"]',
                '.cost',
                '.amount'
            ]
            
            original_price_selectors = [
                '.original-price',
                '.old-price',
                '.strike-price',
                '.crossed-price',
                'span[class*="original"]',
                'div[class*="original"]',
                'span[class*="old"]',
                'div[class*="old"]'
            ]
            
            # Extract current price from detail page
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text(strip=True)
                    price_match = re.search(r'Rs\s*(\d+(?:,\d+)*)', price_text)
                    if price_match:
                        price_str = price_match.group(1).replace(',', '')
                        try:
                            price = float(price_str)
                            break
                        except ValueError:
                            continue
            
            # Extract original price from detail page
            for selector in original_price_selectors:
                element = soup.select_one(selector)
                if element:
                    original_text = element.get_text(strip=True)
                    original_match = re.search(r'Rs\s*(\d+(?:,\d+)*)', original_text)
                    if original_match:
                        original_str = original_match.group(1).replace(',', '')
                        try:
                            original_price = float(original_str)
                            break
                        except ValueError:
                            continue
            
            return price, original_price
            
        except Exception as e:
            self.logger.error(f"Error extracting detail page prices: {e}")
            return None, None
    
    def _extract_complete_name(self, soup):
        """Extract complete medicine name (original logic)"""
        try:
            # Multiple selectors for complete name
            name_selectors = [
                'h1',
                '.product-title',
                '.medicine-title',
                '.product-name',
                '.medicine-name',
                'title'
            ]
            
            for selector in name_selectors:
                element = soup.select_one(selector)
                if element:
                    name = element.get_text(strip=True)
                    if name and len(name) > 3:  # Basic validation
                        return name
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting complete name: {e}")
            return None
    
    def _extract_generic_name(self, soup):
        """Extract generic name with enhanced selectors"""
        try:
            # Enhanced selectors for generic information
            generic_selectors = [
                '.generic-name',
                '.generic-info',
                '.active-ingredient',
                '.ingredient',
                '.drug-ingredient',
                'span:contains("Generic")',
                'div:contains("Generic")',
                'span:contains("Active")',
                'div:contains("Active")',
                'span:contains("Ingredient")',
                'div:contains("Ingredient")',
                '.product-description',
                '.medicine-description'
            ]
            
            for selector in generic_selectors:
                element = soup.select_one(selector)
                if element:
                    generic = element.get_text(strip=True)
                    if generic and len(generic) > 3:
                        # Clean up generic name
                        generic = re.sub(r'^Generic\s*:\s*', '', generic, flags=re.IGNORECASE)
                        generic = re.sub(r'^Active\s*:\s*', '', generic, flags=re.IGNORECASE)
                        generic = re.sub(r'^Ingredient\s*:\s*', '', generic, flags=re.IGNORECASE)
                        return generic.strip()
            
            # Try to find generic name in text content with enhanced patterns
            text_content = soup.get_text()
            generic_patterns = [
                r'Generic[:\s]+([^,\n\r]+)',
                r'Active[:\s]+([^,\n\r]+)',
                r'Ingredient[:\s]+([^,\n\r]+)',
                r'Contains[:\s]+([^,\n\r]+)',
                r'Composition[:\s]+([^,\n\r]+)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\([A-Za-z\s]+\d+[a-z]*\)',  # Pattern like "Diclofenac Sodium (75mg)"
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\d+[a-z]*',  # Pattern like "Diclofenac Sodium 75mg"
            ]
            
            for pattern in generic_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    if match and len(match.strip()) > 3:
                        return match.strip()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting generic name: {e}")
            return None
    
    def _extract_generic_ref_link(self, soup):
        """Extract generic reference link"""
        try:
            # Look for generic links
            generic_link_selectors = [
                'a[href*="/generic/"]',
                'a[href*="generic"]',
                '.generic-link a',
                'a[href*="ingredient"]'
            ]
            
            for selector in generic_link_selectors:
                link = soup.select_one(selector)
                if link:
                    href = link.get('href')
                    if href:
                        return urljoin(self.base_url, href)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting generic ref link: {e}")
            return None
    
    def scrape_letter(self, letter):
        """Scrape all medicines for a specific letter"""
        letter_url = f"{self.base_url}/all-medicines/{letter.lower()}"
        self.logger.info(f"Starting to scrape letter: {letter}")
        
        try:
            # Get medicine links and basic data from listing page
            medicine_data_list = self._extract_medicine_links(letter_url)
            
            if not medicine_data_list:
                self.logger.warning(f"No medicine links found for letter {letter}")
                return
            
            # Process each medicine
            for medicine_data in medicine_data_list:
                try:
                    self._process_medicine(medicine_data)
                    self.stats['total_processed'] += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing medicine {medicine_data.get('url', 'unknown')}: {e}")
                    continue
            
            self.logger.info(f"Completed scraping letter {letter}")
            
        except Exception as e:
            self.logger.error(f"Error scraping letter {letter}: {e}")
    
    def _process_medicine(self, medicine_data):
        """Process individual medicine"""
        try:
            medicine_url = medicine_data['url']
            
            # Extract external ID
            external_id = self._extract_external_id(medicine_url)
            
            # Check if medicine already exists
            if self.db_handler.medicine_exists(external_id):
                self.logger.info(f"Medicine already exists: {external_id}")
                return
            
            # Extract detailed medicine data from detail page
            detail_data = self._extract_medicine_data(medicine_url, medicine_data)
            if not detail_data:
                self.logger.warning(f"Could not extract data for: {medicine_url}")
                return
            
            # Download image if available
            image_path = None
            if detail_data.get('image_url'):
                # We'll download image after getting the system ID
                image_url = detail_data['image_url']
            else:
                image_url = None
            
            # Insert into database
            system_id = self.db_handler.insert_medicine(
                external_id=external_id,
                complete_name=detail_data.get('complete_name'),
                brand_name=detail_data.get('brand_name'),
                generic_name=detail_data.get('generic_name'),
                pack_size=detail_data.get('pack_size'),
                listing_price=detail_data.get('listing_price'),
                listing_original_price=detail_data.get('listing_original_price'),
                detail_price=detail_data.get('detail_price'),
                detail_original_price=detail_data.get('detail_original_price'),
                generic_ref_link=detail_data.get('generic_ref_link'),
                drug_external_link=detail_data.get('drug_external_link'),
                image_path=None  # Will update after image download
            )
            
            # Download image if available
            if image_url and system_id:
                image_filename = self.image_downloader.download_image(
                    image_url, system_id, self.base_url
                )
                
                if image_filename:
                    # Update database with image path
                    self.db_handler.update_medicine(
                        external_id=external_id,
                        complete_name=detail_data.get('complete_name'),
                        brand_name=detail_data.get('brand_name'),
                        generic_name=detail_data.get('generic_name'),
                        pack_size=detail_data.get('pack_size'),
                        listing_price=detail_data.get('listing_price'),
                        listing_original_price=detail_data.get('listing_original_price'),
                        detail_price=detail_data.get('detail_price'),
                        detail_original_price=detail_data.get('detail_original_price'),
                        generic_ref_link=detail_data.get('generic_ref_link'),
                        drug_external_link=detail_data.get('drug_external_link'),
                        image_path=image_filename
                    )
                    self.stats['images_downloaded'] += 1
            
            self.stats['new_medicines'] += 1
            self.logger.info(f"Successfully processed: {external_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing medicine {medicine_url}: {e}")
            raise
    
    def scrape_all_letters(self):
        """Scrape all letters A-Z"""
        letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]
        
        self.logger.info("Starting to scrape all letters A-Z")
        
        for letter in letters:
            try:
                self.scrape_letter(letter)
                
                # Add longer delay between letters
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                self.logger.error(f"Error scraping letter {letter}: {e}")
                continue
        
        self.logger.info("Completed scraping all letters")
        self._print_final_stats()
    
    def _print_final_stats(self):
        """Print final scraping statistics"""
        self.logger.info("=" * 50)
        self.logger.info("SCRAPING COMPLETED - FINAL STATISTICS")
        self.logger.info("=" * 50)
        self.logger.info(f"Total medicines processed: {self.stats['total_processed']}")
        self.logger.info(f"New medicines added: {self.stats['new_medicines']}")
        self.logger.info(f"Medicines updated: {self.stats['updated_medicines']}")
        self.logger.info(f"Images downloaded: {self.stats['images_downloaded']}")
        self.logger.info(f"Failed requests: {self.stats['failed_requests']}")
        
        # Database statistics
        db_stats = self.db_handler.get_statistics()
        if db_stats:
            self.logger.info(f"Total medicines in database: {db_stats['total_medicines']}")
            self.logger.info(f"Medicines with images: {db_stats['medicines_with_images']}")
            self.logger.info(f"Medicines with generic names: {db_stats['medicines_with_generic_names']}")
            self.logger.info(f"Medicines with listing prices: {db_stats['medicines_with_listing_prices']}")
            self.logger.info(f"Medicines with detail prices: {db_stats['medicines_with_detail_prices']}")
        
        # Image statistics
        img_stats = self.image_downloader.get_image_stats()
        self.logger.info(f"Total images on disk: {img_stats['total_images']}")
        self.logger.info(f"Total image size: {img_stats['total_size_mb']} MB")
        self.logger.info("=" * 50) 