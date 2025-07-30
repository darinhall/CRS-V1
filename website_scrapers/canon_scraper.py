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
        """Finds individual product pages for camera bodies using Playwright with Load More functionality"""
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
                    
                    # Use the new _scrape_with_load_more method that handles pagination
                    new_urls = self._scrape_with_load_more(target_url, max_load_more=3)
                    camera_urls.extend(new_urls)
                    
                    print(f"  Found {len(new_urls)} products on {target_url}")
                    
                    # Debug: Print first few links found
                    if new_urls:
                        print(f"  Sample URLs: {new_urls[:3]}")
                        
                    if camera_urls:  # If we found URLs, we can stop
                        break
                        
                except Exception as e:
                    print(f"Error accessing {target_url}: {e}")
                    continue
            
            unique_urls = list(set(camera_urls))
            print(f"\n📊 Pagination Summary:")
            print(f"  Total unique products found: {len(unique_urls)}")
            print(f"  Returning first 50 products for HTML saving")
            return unique_urls[0:50]  # Return up to 50 unique URLs
            
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


    def _scrape_with_load_more(self, url, max_load_more=10):
        """Scrape product URLs from a page with comprehensive pagination checking"""
        product_urls = []
        
        try:
            # Start browser if not already started
            if not self.page:
                self.start_browser()
            
            print(f"Navigating to: {url}")
            self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)  # Wait for content to load
            
            # Get initial page content
            page_content = self.page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Extract product links from initial page
            initial_products = self._extract_product_links(soup, url)
            product_urls.extend(initial_products)
            print(f"  Found {len(initial_products)} products on initial page")
            
            # Track pagination progress
            current_page = 1
            total_pages_found = 0
            
            # First, try URL-based pagination (more reliable)
            print(f"  Checking URL-based pagination...")
            url_pagination_products = self._scrape_url_pagination(url, max_load_more)
            if url_pagination_products:
                product_urls.extend(url_pagination_products)
                print(f"  Found {len(url_pagination_products)} additional products via URL pagination")
            
            # Then try button-based pagination as backup
            print(f"  Checking button-based pagination...")
            button_pagination_products = self._scrape_button_pagination(url, max_load_more)
            if button_pagination_products:
                # Only add products not already found
                new_products = [p for p in button_pagination_products if p not in product_urls]
                product_urls.extend(new_products)
                print(f"  Found {len(new_products)} additional products via button pagination")
            
            print(f"  Total unique products found: {len(product_urls)}")
            
        except Exception as e:
            print(f"Error in _scrape_with_load_more: {e}")
        
        return product_urls

    def _scrape_url_pagination(self, base_url, max_pages=10):
        """Scrape products using URL-based pagination (?p=2, ?p=3, etc.)"""
        all_products = []
        
        try:
            for page_num in range(2, max_pages + 2):  # Start from page 2 (page 1 is base_url)
                page_url = f"{base_url}?p={page_num}"
                print(f"    Checking page {page_num}: {page_url}")
                
                try:
                    self.page.goto(page_url, wait_until='domcontentloaded', timeout=20000)
                    time.sleep(2)
                    
                    page_content = self.page.content()
                    soup = BeautifulSoup(page_content, 'html.parser')
                    
                    # Check if page has products (not a 404 or empty page)
                    products_on_page = self._extract_product_links(soup, page_url)
                    
                    if products_on_page:
                        all_products.extend(products_on_page)
                        print(f"      Found {len(products_on_page)} products on page {page_num}")
                    else:
                        print(f"      No products found on page {page_num} - stopping pagination")
                        break
                        
                except Exception as e:
                    print(f"      Error accessing page {page_num}: {e}")
                    break
                    
        except Exception as e:
            print(f"Error in _scrape_url_pagination: {e}")
        
        return all_products

    def _scrape_button_pagination(self, url, max_clicks=5):
        """Scrape products using button-based pagination (Load More button)"""
        all_products = []
        
        try:
            # Navigate to the base URL
            self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # Get initial page content
            page_content = self.page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Extract initial products
            initial_products = self._extract_product_links(soup, url)
            all_products.extend(initial_products)
            
            # Look for and handle "Load More" button
            load_more_count = 0
            while load_more_count < max_clicks:
                # Find "Load More" button using Playwright
                load_more_button = self._find_load_more_button_playwright()
                
                if not load_more_button:
                    print(f"    No more 'Load More' button found after {load_more_count} clicks")
                    break
                
                # Click "Load More" button
                print(f"    Clicking 'Load More' button (attempt {load_more_count + 1})")
                try:
                    load_more_button.click()
                    time.sleep(3)  # Wait for new content to load
                    
                    # Get updated page content
                    page_content = self.page.content()
                    soup = BeautifulSoup(page_content, 'html.parser')
                    
                    # Extract new product links
                    all_current_products = self._extract_product_links(soup, url)
                    new_products = [p for p in all_current_products if p not in all_products]
                    
                    if new_products:
                        all_products.extend(new_products)
                        print(f"      Loaded {len(new_products)} more products (total: {len(all_products)})")
                        load_more_count += 1
                        time.sleep(2)  # Be respectful
                    else:
                        print(f"      No new products loaded after click")
                        break
                        
                except Exception as e:
                    print(f"      Error clicking 'Load More' button: {e}")
                    break
                    
        except Exception as e:
            print(f"Error in _scrape_button_pagination: {e}")
        
        return all_products


    def _find_load_more_button(self, soup):
        """Find 'Load More' button in the page"""
        # Canon-specific selectors for "Load More" buttons
        load_more_selectors = [
            'button[class*="amscroll-load-button"]',  # Canon's specific class
            'button[class*="load-more"]',
            'button[class*="loadmore"]',
            'a[class*="load-more"]',
            'a[class*="loadmore"]',
            'button:contains("Load More")',
            'a:contains("Load More")',
            '[data-action="load-more"]',
            '[id*="load-more"]',
            '[class*="load-more"]',
            '[class*="amscroll"]'  # Any amscroll-related elements
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

    def _find_load_more_button_playwright(self):
        """Find 'Load More' button using Playwright"""
        try:
            # Canon-specific selectors for "Load More" buttons
            load_more_selectors = [
                'button[class*="amscroll-load-button"]',  # Canon's specific class
                'button[class*="load-more"]',
                'button[class*="loadmore"]',
                'button:has-text("Load more")',
                'button:has-text("Load More")',
                '[class*="amscroll"]:has-text("Load more")',
                '[class*="amscroll"]:has-text("Load More")'
            ]
            
            for selector in load_more_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button:
                        # Check if button is visible and clickable
                        if button.is_visible() and button.is_enabled():
                            return button
                except:
                    continue
            
            # Also look for buttons with "Load More" text using text content
            buttons = self.page.query_selector_all('button')
            for button in buttons:
                try:
                    text = button.text_content().lower()
                    if 'load more' in text and button.is_visible() and button.is_enabled():
                        return button
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error finding load more button: {e}")
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
        
        unique_urls = list(set(lens_urls))
        print(f"\n📊 Lens Pagination Summary:")
        print(f"  Total unique lens products found: {len(unique_urls)}")
        print(f"  Returning first 50 lens products for HTML saving")
        return unique_urls[0:50]  # Return up to 50 unique URLs

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
        
        unique_urls = list(set(accessory_urls))
        print(f"\n📊 Accessory Pagination Summary:")
        print(f"  Total unique accessory products found: {len(unique_urls)}")
        print(f"  Returning first 50 accessory products for HTML saving")
        return unique_urls[0:50]  # Return up to 50 unique URLs

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