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
All the below code was created using Claude. Used as a test scraper to see what information may be able to be extracted from Canon's website. 
'''

class CanonDataScraper:
    def __init__(self):
        self.base_url = "https://www.usa.canon.com/shop/p/cameras" #this is a general url, needs to be updated to the specific category of interest
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def find_camera_pages(self, search_terms=['camera', 'lens', 'dslr', 'mirrorless']):
        """Find camera-related pages from sitemap or by crawling"""
        camera_urls = []
        
        # Try to get sitemap first
        sitemap_urls = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/robots.txt"
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url)
                if response.status_code == 200:
                    if 'sitemap' in response.text.lower():
                        urls = self.get_sitemap_urls(sitemap_url)
                        camera_urls.extend([url for url in urls if any(term in url.lower() for term in search_terms)])
                        break
            except:
                continue
        
        # Currently set so if no sitemap, try manual discovery, but need to change to prioritize manual discovery
        if not camera_urls:
            try:
                # Try common camera section URLs
                camera_sections = [
                    f"{self.base_url}/cameras",
                    f"{self.base_url}/products/cameras",
                    f"{self.base_url}/en/cameras"
                ]
                
                for section_url in camera_sections:
                    try:
                        response = self.session.get(section_url)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            links = soup.find_all('a', href=True)
                            for link in links:
                                href = urljoin(section_url, link['href'])
                                if any(term in href.lower() for term in search_terms):
                                    camera_urls.append(href)
                            break
                    except:
                        continue
            except Exception as e:
                print(f"Error in manual discovery: {e}")
        
        return list(set(camera_urls))[0:3]  # Limit to 3 for testing scrape_website_specs
    
    def scrape_website_specs(self, url):
        """Scrape camera specifications from Canon website"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
            
            # Try to find title
            title_selectors = ['h1', '.product-title', '.page-title', 'title']
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
    scraper = CanonDataScraper()
    camera_urls = scraper.find_camera_pages()
    results = []
    for url in camera_urls:
        results.append(scraper.scrape_website_specs(url))
    
    # Save results
    with open('canon_scraping_results.json', 'w') as f:
        json.dump(results, f, indent=2)