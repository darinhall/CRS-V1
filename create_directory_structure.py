#!/usr/bin/env python3
"""
Script to create the new directory structure
"""

import os
from pathlib import Path

def create_directory_structure():
    """Create the new directory structure"""
    
    # Define all companies
    companies = [
        "canon", "nikon", "sony", "fuji", "panasonic", "olympus", "leica", 
        "hasselblad", "google", "apple", "dji", "samsung", "gopro", "polaroid", 
        "instax", "kodak", "red", "arri", "blackmagic", "zeiss", "ricoh", 
        "sigma", "pentax", "minolta"
    ]
    
    base_path = Path("/Users/darinhall/Documents/CRS_Database/company_product")
    
    for company in companies:
        # Create raw_html directory
        raw_html_path = base_path / company / "raw_html"
        raw_html_path.mkdir(parents=True, exist_ok=True)
        
        # Create processed_data subdirectories
        processed_data_path = base_path / company / "processed_data"
        (processed_data_path / "body").mkdir(parents=True, exist_ok=True)
        (processed_data_path / "accessory").mkdir(parents=True, exist_ok=True)
        (processed_data_path / "lens").mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Created structure for {company}")
    
    print(f"\n🎉 Created directory structure for {len(companies)} companies!")
    
    # Show the structure
    print(f"\n📁 Directory structure:")
    for company in companies[:5]:  # Show first 5 as example
        print(f"  {company}/")
        print(f"    ├── raw_html/")
        print(f"    └── processed_data/")
        print(f"        ├── body/")
        print(f"        ├── accessory/")
        print(f"        └── lens/")

if __name__ == "__main__":
    create_directory_structure() 