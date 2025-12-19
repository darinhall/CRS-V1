import logging
import json
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from langchain_core.tools import tool
import time
import re

logger = logging.getLogger(__name__)

class ExtractionAgent:
    """
    Agent responsible for extracting specification data from a product page.
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

    def stop_browser(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.playwright = None
        self.browser = None
        self.page = None

    def extract_specs(self, product_url: str) -> Dict[str, Any]:
        """
        Navigates to the product URL and extracts the technical specifications.
        """
        logger.info(f"Extracting specs from {product_url}")
        self.start_browser()
        
        raw_data = {"url": product_url, "specs": {}, "raw_html": ""}
        
        try:
            self.page.goto(product_url, wait_until='domcontentloaded')
            time.sleep(2) # Wait for dynamic content
            
            # Click "Specs" tab if it exists (common pattern)
            try:
                specs_tab = self.page.get_by_text("Specifications", exact=False).first
                if specs_tab.is_visible():
                    specs_tab.click()
                    time.sleep(1)
            except:
                pass

            content = self.page.content()
            raw_data["raw_html"] = content
            
            # Parse using BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Use the robust parsing logic (simplified here)
            # In a real scenario, we would inject the specific parser strategy here
            specs = self._parse_canon_specs(soup)
            raw_data["specs"] = specs
            
        except Exception as e:
            logger.error(f"Error extracting specs: {e}")
            raw_data["error"] = str(e)
        finally:
            self.stop_browser()
            
        return raw_data

    def _parse_canon_specs(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Adapted from CanonMirrorlessParser.
        """
        specs = {}
        
        # Try to find the tech-spec-data div
        tech_spec_div = soup.find('div', id='tech-spec-data')
        if not tech_spec_div:
            # Fallback for other structures
            return {}

        # Find attribution groups
        groups = tech_spec_div.find_all('h3')
        for group in groups:
            group_name = group.get_text(strip=True)
            specs[group_name] = {}
            
            # Find parent container
            container = group.find_parent('div', class_='tech-spec')
            if container:
                attrs = container.find_all('div', class_='tech-spec-attr')
                # Process in pairs
                for i in range(0, len(attrs), 2):
                    if i + 1 < len(attrs):
                        key = attrs[i].get_text(strip=True)
                        val_div = attrs[i+1]
                        
                        # Handle tables
                        if val_div.find('table'):
                            # Simple table extraction
                            val = "[Table Data]" 
                        else:
                            val = val_div.get_text(strip=True)
                            
                        specs[group_name][key] = val
                        
        return specs

@tool
def extract_product_specs(product_url: str) -> str:
    """
    Extract technical specifications from a product URL.
    Returns a JSON string containing the extracted data.
    """
    agent = ExtractionAgent()
    data = agent.extract_specs(product_url)
    # Remove raw_html to keep the response size manageable for the agent
    if "raw_html" in data:
        del data["raw_html"]
    return json.dumps(data, indent=2)
