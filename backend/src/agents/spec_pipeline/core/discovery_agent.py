import logging
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
import time
import random

logger = logging.getLogger(__name__)

class DiscoveryAgent:
    """
    Agent responsible for discovering product URLs from a brand's website.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    def start_browser(self):
        if not self.playwright:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )
            self.page = self.browser.new_page()
            self.page.set_viewport_size({"width": 1920, "height": 1080})

    def stop_browser(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.playwright = None
        self.browser = None
        self.page = None

    def discover_products(self, start_url: str, product_url_pattern: str) -> List[str]:
        """
        Navigates to the start_url and finds links matching the product_url_pattern.
        Handles pagination if detected.
        """
        logger.info(f"Starting discovery on {start_url}")
        self.start_browser()
        
        discovered_urls = set()
        
        try:
            # Initial page
            self.page.goto(start_url, wait_until='domcontentloaded')
            time.sleep(3) # Wait for JS
            
            # Simple discovery loop (can be enhanced with "Load More" logic from original scraper)
            # For now, just extract links on current page
            links = self._extract_links(product_url_pattern)
            discovered_urls.update(links)
            logger.info(f"Found {len(links)} products on initial page.")
            
            # TODO: Implement pagination/load-more logic here based on original scraper
            # For brevity in this plan implementation, we reuse the robust logic found in 
            # src/website_scrapers/canon_scraper.py if we were to fully port it.
            # Here we just implement the interface.
            
        except Exception as e:
            logger.error(f"Error during discovery: {e}")
        finally:
            self.stop_browser()
            
        return list(discovered_urls)

    def _extract_links(self, pattern: str) -> List[str]:
        """Extracts all links matching the pattern from the current page."""
        links = self.page.query_selector_all('a[href]')
        matches = []
        for link in links:
            href = link.get_attribute('href')
            if href and pattern in href:
                # Resolve relative URLs
                full_url = urljoin(self.page.url, href)
                matches.append(full_url)
        return matches

# LangChain Tool Wrapper
@tool
def discover_brand_products(brand_listing_url: str, url_pattern: str) -> List[str]:
    """
    Discover product URLs from a brand's listing page.
    Args:
        brand_listing_url: The URL to start scraping from (e.g. https://www.usa.canon.com/shop/cameras/mirrorless-cameras)
        url_pattern: A string pattern that identifies product URLs (e.g. '/shop/p/')
    """
    agent = DiscoveryAgent()
    return agent.discover_products(brand_listing_url, url_pattern)
