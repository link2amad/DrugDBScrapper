import os
import requests
import logging
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin, urlparse
import time
import random

class ImageDownloader:
    def __init__(self, images_dir="data/images"):
        self.images_dir = images_dir
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # Create images directory if it doesn't exist
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Set up session headers for anti-blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def download_image(self, image_url, system_id, base_url=None):
        """
        Download and save image with anti-blocking measures
        
        Args:
            image_url: URL of the image to download
            system_id: System ID to use as filename
            base_url: Base URL for relative image URLs
            
        Returns:
            str: Path to saved image or None if failed
        """
        try:
            # Handle relative URLs
            if not image_url.startswith(('http://', 'https://')):
                if base_url:
                    image_url = urljoin(base_url, image_url)
                else:
                    self.logger.warning(f"Cannot resolve relative URL: {image_url}")
                    return None
            
            # Add random delay to avoid blocking
            time.sleep(random.uniform(0.5, 2.0))
            
            # Download image with timeout and retry logic
            response = self.session.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Validate content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                self.logger.warning(f"URL does not point to an image: {content_type}")
                return None
            
            # Read image data
            image_data = response.content
            
            # Validate image using PIL
            try:
                image = Image.open(BytesIO(image_data))
                image.verify()  # Verify image integrity
                
                # Determine file extension
                image_format = image.format.lower() if image.format else 'jpeg'
                file_extension = image_format if image_format in ['jpeg', 'png', 'gif', 'bmp'] else 'jpg'
                
            except Exception as e:
                self.logger.warning(f"Invalid image data: {e}")
                return None
            
            # Generate filename
            filename = f"{system_id}.{file_extension}"
            filepath = os.path.join(self.images_dir, filename)
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            self.logger.info(f"Image downloaded successfully: {filename}")
            return filename
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download image {image_url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error downloading image {image_url}: {e}")
            return None
    
    def extract_image_url(self, soup, base_url):
        """
        Extract image URL from BeautifulSoup object
        
        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL for relative image URLs
            
        Returns:
            str: Image URL or None if not found
        """
        try:
            # Try multiple selectors for image extraction
            image_selectors = [
                'img[src*="medicine"]',  # Images with "medicine" in src
                'img[src*="product"]',   # Images with "product" in src
                '.product-image img',    # Product image class
                '.medicine-image img',   # Medicine image class
                'img[alt*="medicine"]',  # Images with "medicine" in alt
                'img[alt*="drug"]',      # Images with "drug" in alt
                'img[src*=".jpg"]',      # JPG images
                'img[src*=".png"]',      # PNG images
                'img[src*=".jpeg"]',     # JPEG images
                'img'                    # Any image as fallback
            ]
            
            for selector in image_selectors:
                img_tag = soup.select_one(selector)
                if img_tag and img_tag.get('src'):
                    src = img_tag.get('src')
                    
                    # Skip placeholder images
                    if any(skip in src.lower() for skip in ['placeholder', 'no-image', 'default']):
                        continue
                    
                    # Handle relative URLs
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(base_url, src)
                    
                    return src
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting image URL: {e}")
            return None
    
    def cleanup_orphaned_images(self, valid_system_ids):
        """
        Remove images that don't correspond to valid system IDs
        
        Args:
            valid_system_ids: List of valid system IDs
        """
        try:
            if not os.path.exists(self.images_dir):
                return
            
            for filename in os.listdir(self.images_dir):
                if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    # Extract system ID from filename
                    try:
                        system_id = int(filename.split('.')[0])
                        if system_id not in valid_system_ids:
                            filepath = os.path.join(self.images_dir, filename)
                            os.remove(filepath)
                            self.logger.info(f"Removed orphaned image: {filename}")
                    except ValueError:
                        # Skip files that don't follow naming convention
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error cleaning up orphaned images: {e}")
    
    def get_image_stats(self):
        """
        Get statistics about downloaded images
        
        Returns:
            dict: Image statistics
        """
        try:
            if not os.path.exists(self.images_dir):
                return {'total_images': 0, 'total_size_mb': 0}
            
            total_images = 0
            total_size = 0
            
            for filename in os.listdir(self.images_dir):
                if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    filepath = os.path.join(self.images_dir, filename)
                    total_images += 1
                    total_size += os.path.getsize(filepath)
            
            return {
                'total_images': total_images,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting image stats: {e}")
            return {'total_images': 0, 'total_size_mb': 0} 