import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from urllib.parse import urljoin, urlparse
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright


'''
This is a scraper for the Canon website. It is used to scrape the main canon shop page to find all the items on Canon's website currently for sale.
'''

class CanonDataScraper:
    def __init__(self):
        self.base_url = "https://www.usa.canon.com/shop/" #general url used for canon website
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Initialize Playwright for JavaScript-heavy sites
        self.playwright = None
        self.browser = None
        self.page = None

    def start_browser(self):
        """Start Playwright browser"""
        if not self.playwright:
            self.playwright = sync_playwright().start()
            # Use more realistic browser settings
            self.browser = self.playwright.chromium.launch(
                headless=False,  # Show browser for debugging
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            self.page = self.browser.new_page()
            
            # Set more realistic headers
            self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            })
            
            # Set viewport to look more realistic
            self.page.set_viewport_size({"width": 1920, "height": 1080})

    def stop_browser(self):
        """Stop Playwright browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def find_body_pages(self):
        """Finds individual product pages for camera bodies using Playwright"""
        camera_urls = []
        
        try:
            # Start browser
            self.start_browser()
            
            # Target specific Canon product pages
            target_urls = [
                "https://www.usa.canon.com/shop/digital-cameras",
                "https://www.usa.canon.com/shop/digital-cameras/mirrorless-cameras",
                "https://www.usa.canon.com/shop/digital-cameras/dslr-cameras",
                "https://www.usa.canon.com/shop/digital-cameras/point-and-shoot-cameras"
            ]

            for target_url in target_urls:
                try:
                    print(f"Scraping from: {target_url}")
                    
                    # Navigate to the page
                    self.page.goto(target_url, wait_until='domcontentloaded', timeout=30000)  # Reduced timeout
                    
                    # Wait for content to load
                    time.sleep(3)
                    
                    # Get page content after JavaScript loads
                    page_content = self.page.content()
                    soup = BeautifulSoup(page_content, 'html.parser')
                    
                    # Debug: Print page title and some content
                    print(f"  Page title: {soup.title.string if soup.title else 'No title'}")
                    print(f"  Total links found: {len(soup.find_all('a'))}")
                    
                    # Extract product links
                    new_urls = self._extract_product_links(soup, target_url)
                    camera_urls.extend(new_urls)
                    
                    print(f"  Found {len(new_urls)} products on {target_url}")
                    
                    # Debug: Print first few links found
                    if new_urls:
                        print(f"  Sample URLs: {new_urls[:3]}")
                    else:
                        # Look for any links to understand the structure
                        all_links = soup.find_all('a', href=True)
                        print(f"  Sample links found: {[link.get('href') for link in all_links[:5]]}")
                        
                    if camera_urls:  # If we found URLs, we can stop
                        break
                        
                except Exception as e:
                    print(f"Error accessing {target_url}: {e}")
                    continue
            
            return list(set(camera_urls))[0:20]  # Return up to 20 unique URLs
            
        except Exception as e:
            print(f"Error in find_body_pages: {e}")
            return []

    def _extract_product_links(self, soup, base_url):
        """Extract product URLs from page HTML"""
        product_urls = []
        
        # Look for links with class "product-item-link"
        product_links = soup.find_all('a', class_='product-item-link')
        
        for link in product_links:
            href = link.get('href')
            if href:
                # Make sure it's a full URL
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                else:
                    full_url = href
                # Only include actual product pages (not filter pages) and exclude refurbished
                if '/shop/p/' in full_url and '?' not in full_url and 'refurbished' not in full_url.lower():
                    product_urls.append(full_url)
        
        # Also look for any links that contain the product pattern
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            if href and ('/shop/p/' in href or href.startswith('/shop/p/')):
                # Make sure it's a full URL
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                else:
                    full_url = href
                # Only include actual product pages (not filter pages) and exclude refurbished
                if '/shop/p/' in full_url and '?' not in full_url and 'refurbished' not in full_url.lower() and full_url not in product_urls:
                    product_urls.append(full_url)
        
        # Look for product links in different formats
        product_selectors = [
            'a[href*="/shop/p/"]',
            'a[class*="product"]',
            'a[class*="item"]'
        ]
        
        for selector in product_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    if href.startswith('/'):
                        full_url = urljoin(base_url, href)
                    else:
                        full_url = href
                    # Only include actual product pages (not filter pages) and exclude refurbished
                    if '/shop/p/' in full_url and '?' not in full_url and 'refurbished' not in full_url.lower() and full_url not in product_urls:
                        product_urls.append(full_url)
        
        return product_urls

    def save_product_html(self, url, output_dir="canon_html_pages", max_retries=2):
        """Save the HTML of a product page to a local file with retry logic"""
        for attempt in range(max_retries):
            try:
                # Create output directory if it doesn't exist
                Path(output_dir).mkdir(exist_ok=True)
                
                # Use Playwright to get the page
                if not self.page:
                    self.start_browser()
                
                print(f"Saving HTML from: {url} (attempt {attempt + 1}/{max_retries})")
                
                # Increase timeout for slower pages
                timeout = 25000 if attempt == 0 else 30000  # Longer timeout on retry
                
                self.page.goto(url, wait_until='domcontentloaded', timeout=timeout)
                time.sleep(3)  # Wait for content to load
                
                page_content = self.page.content()
                
                # Create a safe filename from the URL
                # Extract product name from URL
                product_name = url.split('/')[-1].split('?')[0].split('#')[0]
                if not product_name:
                    product_name = "product"
                
                # Create filename
                filename = f"{product_name}.html"
                filepath = Path(output_dir) / filename
                
                # Save HTML to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(page_content)
                
                print(f"  ✅ Saved: {filepath}")
                return str(filepath)
                
            except Exception as e:
                print(f"  ❌ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"  🔄 Retrying...")
                    time.sleep(2)  # Wait before retry
                else:
                    print(f"  �� Failed after {max_retries} attempts")
                    return None
        
        return None

    def save_all_product_html(self, urls, output_dir="canon_html_pages"):
        """Save HTML for all product URLs with better tracking"""
        saved_files = []
        failed_urls = []
        
        try:
            # Start browser once for all pages
            self.start_browser()
            
            for i, url in enumerate(urls, 1):
                print(f"\nProcessing {i}/{len(urls)}: {url}")
                saved_file = self.save_product_html(url, output_dir)
                if saved_file:
                    saved_files.append(saved_file)
                else:
                    failed_urls.append(url)
                
                # Add delay between requests
                time.sleep(1)
            
            print(f"\n�� Summary:")
            print(f"  ✅ Successfully saved: {len(saved_files)} files")
            print(f"  ❌ Failed to save: {len(failed_urls)} files")
            print(f"  📁 Location: {output_dir}/")
            
            if failed_urls:
                print(f"\n❌ Failed URLs:")
                for url in failed_urls:
                    print(f"  - {url}")
            
            return saved_files
            
        except Exception as e:
            print(f"Error in save_all_product_html: {e}")
            return saved_files
        finally:
            self.stop_browser()

    # Finds individual product pages for camera lenses
    def find_lens_pages(self, search_terms=['EF', 'RF', 'lens', 'EF-S'], max_load_more=5):
        """Find lens-related pages by handling 'Load More' buttons and specific product links"""
        lens_urls = []
        
        # Target specific Canon product pages
        target_urls = [
            "https://www.usa.canon.com/shop/lenses/ef-lenses",
            "https://www.usa.canon.com/shop/lenses/rf-lenses",
            "https://www.usa.canon.com/shop/lenses/ef-s-lenses",
            "https://www.usa.canon.com/shop/lenses/lenses"
        ]
        
        for target_url in target_urls:
            try:
                print(f"Scraping from: {target_url}")
                lens_urls.extend(self._scrape_with_load_more(target_url, max_load_more))
                
                if lens_urls:  # If we found URLs, we can stop
                    break

            except Exception as e:
                print(f"Error accessing {target_url}: {e}")
                continue
        
        return list(set(lens_urls))[0:20]  # Return up to 20 unique URLs

    # Finds individual product pages for camera accessories
    def find_accessory_pages(self, search_terms=['accessory', 'accessories', 'accessory kit', 'accessory set'], max_load_more=5):
        """Find accessory-related pages by handling 'Load More' buttons and specific product links"""
        accessory_urls = []
        
        # Target specific Canon product pages
        target_urls = [
            "https://www.usa.canon.com/shop/accessories/accessories",
            "https://www.usa.canon.com/shop/accessories/accessory-kits",
            "https://www.usa.canon.com/shop/accessories/accessory-sets",
            "https://www.usa.canon.com/shop/accessories/lenses",
            "https://www.usa.canon.com/shop/accessories/lenses/ef-lenses",
            "https://www.usa.canon.com/shop/accessories/lenses/rf-lenses",
            "https://www.usa.canon.com/shop/accessories/lenses/ef-s-lenses",
            "https://www.usa.canon.com/shop/accessories/lenses/lenses"
        ]
        
        for target_url in target_urls:
            try:
                print(f"Scraping from: {target_url}")
                accessory_urls.extend(self._scrape_with_load_more(target_url, max_load_more))
                
                if accessory_urls:  # If we found URLs, we can stop
                    break
                
            except Exception as e:
                print(f"Error accessing {target_url}: {e}")
                continue
        
        return list(set(accessory_urls))[0:20]  # Return up to 20 unique URLs

    def _scrape_with_load_more(self, url, max_load_more=5):
        """Scrape product URLs from a page with 'Load More' functionality"""
        product_urls = []
        
        try:
            # Get the initial page
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product links from initial page
            product_urls.extend(self._extract_product_links(soup, url))
            print(f"  Found {len(product_urls)} products on initial page")
            
            # Look for and handle "Load More" button
            load_more_count = 0
            while load_more_count < max_load_more:
                # Find "Load More" button
                load_more_button = self._find_load_more_button(soup)
                
                if not load_more_button:
                    print(f"  No more 'Load More' button found after {load_more_count} clicks")
                    break
                
                # Click "Load More" (simulate AJAX request)
                new_products = self._handle_load_more(url, load_more_count + 1)
                if new_products:
                    product_urls.extend(new_products)
                    print(f"  Loaded {len(new_products)} more products (total: {len(product_urls)})")
                    load_more_count += 1
                    time.sleep(2)  # Be respectful
                else:
                    print(f"  No more products loaded after {load_more_count} clicks")
                    break
            
        except Exception as e:
            print(f"Error in _scrape_with_load_more: {e}")
        
        return product_urls


    def _find_load_more_button(self, soup):
        """Find 'Load More' button in the page"""
        # Common selectors for "Load More" buttons
        load_more_selectors = [
            'button[class*="load-more"]',
            'button[class*="loadmore"]',
            'a[class*="load-more"]',
            'a[class*="loadmore"]',
            'button:contains("Load More")',
            'a:contains("Load More")',
            '[data-action="load-more"]',
            '[id*="load-more"]',
            '[class*="load-more"]'
        ]
        
        for selector in load_more_selectors:
            button = soup.select_one(selector)
            if button:
                return button
        
        # Also look for buttons with "Load More" text
        buttons = soup.find_all(['button', 'a'])
        for button in buttons:
            if 'load more' in button.get_text().lower():
                return button
        
        return None

    def _handle_load_more(self, base_url, page_number):
        """Handle the AJAX request for loading more products"""
        try:
            # Common patterns for "Load More" AJAX endpoints
            ajax_patterns = [
                f"{base_url}?page={page_number}",
                f"{base_url}?p={page_number}",
                f"{base_url}?offset={page_number * 12}",  # Common offset pattern
                f"{base_url}?limit={page_number * 12}",
            ]
            
            for ajax_url in ajax_patterns:
                try:
                    response = self.session.get(ajax_url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        new_products = self._extract_product_links(soup, base_url)
                        if new_products:
                            return new_products
                except:
                    continue
            
            return []
            
        except Exception as e:
            print(f"Error handling load more: {e}")
            return []
    
    def scrape_website_specs(self, url):
        """Scrape camera specifications from Canon website using Playwright"""
        try:
            # Use Playwright instead of requests to avoid 403 errors
            if not self.page:
                self.start_browser()
            
            print(f"Scraping specs from: {url}")
            self.page.goto(url, wait_until='networkidle')
            time.sleep(2)  # Wait for content to load
            
            page_content = self.page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Extract basic info
            product_data = {
                'url': url,
                'title': '',
                'model': '',
                'type': '',
                'specifications': {},
                'images': [],
                'price': '',
                'description': ''
            }
            
            # Finding the title of the product
            title_selectors = ['h1', '.product-title', '.page-title', 'title', '.product-item-name']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    product_data['title'] = title_elem.get_text().strip()
                    break

            # Look for specifications tables/sections
            spec_sections = soup.find_all(['table', 'div'], class_=re.compile(r'spec|specification|feature|detail', re.I))
            
            for section in spec_sections:
                # Extract table data
                rows = section.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text().strip()
                        value = cells[1].get_text().strip()
                        if key and value:
                            product_data['specifications'][key] = value
                
                # Extract list data
                items = section.find_all('li')
                for item in items:
                    text = item.get_text().strip()
                    if ':' in text:
                        key, value = text.split(':', 1)
                        product_data['specifications'][key.strip()] = value.strip()
            
            # Look for images
            img_tags = soup.find_all('img', src=True)
            for img in img_tags:
                src = img['src']
                if src and not src.startswith('data:'):
                    full_url = urljoin(url, src)
                    product_data['images'].append(full_url)
            
            # Look for price
            price_selectors = ['.price', '.cost', '[class*="price"]', '[class*="cost"]']
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    product_data['price'] = price_elem.get_text().strip()
                    break
            
            # Extract description
            desc_selectors = ['.description', '.overview', '.product-description', 'p']
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem and len(desc_elem.get_text().strip()) > 50:
                    product_data['description'] = desc_elem.get_text().strip()[:500]
                    break

            return product_data
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def test_canon_access(self):
        """Test if we can access Canon's main site"""
        try:
            # Start browser
            self.start_browser()
            
            # Try the main Canon site first
            print("Testing access to main Canon site...")
            self.page.goto("https://www.usa.canon.com", wait_until='domcontentloaded', timeout=30000)  # Reduced timeout
            time.sleep(3)
            
            page_content = self.page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            print(f"Page title: {soup.title.string if soup.title else 'No title'}")
            print(f"Total links: {len(soup.find_all('a'))}")
            
            # Look for any shop links
            shop_links = soup.find_all('a', href=True)
            shop_urls = [link.get('href') for link in shop_links if 'shop' in link.get('href', '').lower()]
            print(f"Shop links found: {shop_urls[:5]}")
            
            return len(shop_urls) > 0
            
        except Exception as e:
            print(f"Error testing Canon access: {e}")
            return False
        # Don't stop browser here - let the main flow manage it

# Usage example
if __name__ == "__main__":
    scraper = CanonDataScraper()  # This calls __init__ automatically
    
    try:
        # Test access first
        print("=== Testing Canon Access ===")
        if scraper.test_canon_access():
            print("✅ Can access Canon website")
            
            print("\n=== Scraping Camera Pages ===")
            camera_urls = scraper.find_body_pages()
            print(f"Found {len(camera_urls)} camera URLs (excluding refurbished)")
            
            if camera_urls:
                print("\n=== Saving HTML Files ===")
                saved_files = scraper.save_all_product_html(camera_urls)
                
                print(f"\n📁 HTML files saved to: canon_html_pages/")
                print(f"📊 Total files saved: {len(saved_files)}")
                
                # Optional: Show some sample filenames
                if saved_files:
                    print("\nSample saved files:")
                    for file in saved_files[:5]:
                        print(f"  - {Path(file).name}")
                
            else:
                print("No camera URLs found")
        else:
            print("❌ Cannot access Canon website - they may be blocking automated access")
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        # Always stop browser at the end
        try:
            scraper.stop_browser()
        except:
            pass  # Ignore errors when stopping browser