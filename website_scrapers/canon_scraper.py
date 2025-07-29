import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from urllib.parse import urljoin, urlparse
import re
from pathlib import Path
import xml.etree.ElementTree as ET

'''
This is a scraper for the Canon website. It is used to scrape the main canon shop page to find all the items on Canon's website currently for sale.
'''

class CanonDataScraper:
    def __init__(self):
        self.base_url = "https://www.usa.canon.com" #general url used for canon website
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def find_body_pages(self):
        """Finds individual product pages for camera bodies, prases through https://www.usa.canon.com/shop/digital-cameras"""
        camera_urls = []
        
        # Get the initial page
        response = self.session.get(self.base_url)
        # response.raise_for_status()  # Comment this out for testing
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Target specific Canon product pages
            target_urls = [
                "https://www.usa.canon.com/shop/digital-cameras"
                "https://www.usa.canon.com/shop/digital-cameras/mirrorless-cameras",
                "https://www.usa.canon.com/shop/digital-cameras/dslr-cameras",
                "https://www.usa.canon.com/shop/digital-cameras/point-and-shoot-cameras"
            ]

            for target_url in target_urls:
                try:
                    print(f"Scraping from: {target_url}")
                    camera_urls.extend(self._extract_product_links(soup, target_url))
                    
                    if camera_urls:  # If we found URLs, we can stop
                        print(f"  Found {len(camera_urls)} products on initial page")
                        break
                        
                except Exception as e:
                    print(f"Error accessing {target_url}: {e}")
                    continue
            
            return list(set(camera_urls))[0:20]  # Return up to 20 unique URLs
        else:
            print(f"Got status code: {response.status_code}")
            return []

    def _extract_product_links(self, soup, base_url):
        """Extract product URLs from main page HTML"""
        product_urls = []
        
        # Look for links with class "product-item-link"
        product_links = soup.find_all('a', class_='product-item-link')
        
        for link in product_links:
            href = link.get('href')
            if href:
                # Check if it's a product page (starts with /shop/p/)
                if 'shop/p/' in href:
                    product_urls.append(href)
        """
        # Also look for any links that contain the product pattern
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            if href and ('/shop/p/' in href or href.startswith('/shop/p/')):
                full_url = urljoin(base_url, href)
                if full_url not in product_urls:
                    product_urls.append(full_url)
        """
        return product_urls

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
        """Scrape camera specifications from Canon website, need to fix for individual product page types (i.e. camera bodies, lenses, etc.)"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info
            product_data = {
                'url': '',
                'title': '',
                'model': '',
                'type': '',
                'specifications': {},
                'images': [],
                'price': '',
                'description': ''
            }
            
            # Finding the url of the product
            url_selectors = ['product-item-link']
            for selector in url_selectors:
                url_elem = soup.select_one(selector)
                if url_elem:
                    product_data['url'] = url_elem.get('href')
                    break

            # Finding the title of the product
            title_selectors = ['product-item-name']
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
    # Scrape up to 10 "Load More" clicks
    camera_urls = scraper.find_body_pages()
    print(f"Found {len(camera_urls)} camera URLs")
    results = []
    for url in camera_urls:
        results.append(scraper.scrape_website_specs(url))
    
    # Save results
    with open('canon_scraping_results.json', 'w') as f:
        json.dump(results, f, indent=2)