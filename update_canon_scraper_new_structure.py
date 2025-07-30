#!/usr/bin/env python3
"""
Script to update canon scraper with new directory structure
"""

def update_canon_scraper():
    """Update the canon scraper with new directory structure"""
    
    # Read the current file
    with open('website_scrapers/canon_scraper.py', 'r') as f:
        content = f.read()
    
    # Update the method signatures and implementations
    content = content.replace(
        'def save_product_html(self, url, output_dir="canon_html_pages", max_retries=2):',
        'def save_product_html(self, url, company="canon", category="body", max_retries=2):'
    )
    
    content = content.replace(
        'def save_all_product_html(self, urls, output_dir="canon_html_pages"):',
        'def save_all_product_html(self, urls, company="canon", category="body"):'
    )
    
    # Update the directory creation
    content = content.replace(
        'Path(output_dir).mkdir(exist_ok=True)',
        'base_dir = "/Users/darinhall/Documents/CRS_Database/company_product"\n                output_dir = f"{base_dir}/{company}/raw_html"\n                Path(output_dir).mkdir(parents=True, exist_ok=True)'
    )
    
    # Update the save_all_product_html call
    content = content.replace(
        'saved_file = self.save_product_html(url, output_dir)',
        'saved_file = self.save_product_html(url, company, category)'
    )
    
    # Update the main execution
    content = content.replace(
        'saved_files = scraper.save_all_product_html(camera_urls)',
        'saved_files = scraper.save_all_product_html(camera_urls, company="canon", category="body")'
    )
    
    # Update the summary location
    content = content.replace(
        'print(f"  📁 Location: {output_dir}/")',
        'print(f"  📁 Location: /Users/darinhall/Documents/CRS_Database/company_product/{company}/raw_html/")'
    )
    
    # Write the updated content back
    with open('website_scrapers/canon_scraper.py', 'w') as f:
        f.write(content)
    
    print("✅ Successfully updated canon_scraper.py with new directory structure!")

if __name__ == "__main__":
    update_canon_scraper() 