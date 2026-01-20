#!/usr/bin/env python3
"""
Helper script to analyze and categorize Canon EOS R files.
This script helps understand which files are mirrorless cameras vs kits/bundles.
"""

import os
from pathlib import Path
from bs4 import BeautifulSoup
import re


def analyze_canon_files():
    """Analyze all Canon EOS R files and categorize them."""
    
    data_dir = Path("data/company_product/canon/raw_html")
    
    # Categories for files
    categories = {
        'mirrorless_cameras': [],
        'lens_kits': [],
        'creator_kits': [],
        'firmware_updates': [],
        'other': []
    }
    
    # Find all EOS R files
    eos_r_files = list(data_dir.glob("eos-r*.html"))
    
    print(f"Found {len(eos_r_files)} EOS R files to analyze")
    print("=" * 80)
    
    for file_path in eos_r_files:
        filename = file_path.stem.lower()
        
        # Categorize based on filename patterns
        if any(pattern in filename for pattern in ['kit', 'mm']):
            if any(pattern in filename for pattern in ['creator', 'content', 'vlogging']):
                categories['creator_kits'].append(file_path)
            else:
                categories['lens_kits'].append(file_path)
        elif any(pattern in filename for pattern in ['firmware', 'cropping', 'stop-motion']):
            categories['firmware_updates'].append(file_path)
        else:
            # Check if it's actually a mirrorless camera
            if has_mirrorless_specifications(file_path):
                categories['mirrorless_cameras'].append(file_path)
            else:
                categories['other'].append(file_path)
    
    # Print results
    print("\n📊 FILE CATEGORIZATION RESULTS:")
    print("=" * 80)
    
    for category, files in categories.items():
        print(f"\n{category.upper().replace('_', ' ')} ({len(files)} files):")
        print("-" * 40)
        
        if files:
            for file_path in sorted(files):
                filename = file_path.stem
                print(f"  • {filename}")
        else:
            print("  (none)")
    
    # Summary statistics
    print(f"\n📈 SUMMARY:")
    print("=" * 80)
    total_files = sum(len(files) for files in categories.values())
    print(f"Total EOS R files: {total_files}")
    print(f"Legitimate mirrorless cameras: {len(categories['mirrorless_cameras'])}")
    print(f"Lens kits: {len(categories['lens_kits'])}")
    print(f"Creator kits: {len(categories['creator_kits'])}")
    print(f"Firmware updates: {len(categories['firmware_updates'])}")
    print(f"Other/uncategorized: {len(categories['other'])}")
    
    # Show examples of each category
    print(f"\n🔍 EXAMPLES BY CATEGORY:")
    print("=" * 80)
    
    for category, files in categories.items():
        if files:
            print(f"\n{category.upper().replace('_', ' ')}:")
            for file_path in sorted(files)[:3]:  # Show first 3 examples
                print(f"  • {file_path.stem}")
            if len(files) > 3:
                print(f"  ... and {len(files) - 3} more")


def has_mirrorless_specifications(file_path):
    """Check if a file contains mirrorless camera specifications or not."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Primary check: specific mirrorless camera specification
        if "Digital interchangeable lens, mirrorless camera" in html_content:
            return True
        
        # Secondary checks: other mirrorless indicators
        mirrorless_indicators = [
            "mirrorless camera",
            "full-frame mirrorless",
            "aps-c mirrorless",
            "eos r",
            "rf mount"
        ]
        
        content_lower = html_content.lower()
        for indicator in mirrorless_indicators:
            if indicator in content_lower:
                return True
        
        return False
        
    except Exception as e:
        print(f"Error reading {file_path.name}: {e}")
        return False


def show_file_details():
    """Show detailed information about specific files."""
    
    data_dir = Path("data/company_product/canon/raw_html")
    
    # Example files to examine
    example_files = [
        "eos-r3.html",
        "eos-r5.html", 
        "eos-r10-rf-s18-45mm-f4-5-6-3-is-stm-lens-kit.html"
    ]
    
    print("\n🔍 DETAILED FILE ANALYSIS:")
    print("=" * 80)
    
    for filename in example_files:
        file_path = data_dir / filename
        if file_path.exists():
            print(f"\n📄 {filename}:")
            print("-" * 40)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Check for mirrorless specifications
                has_mirrorless_spec = "Digital interchangeable lens, mirrorless camera" in html_content
                has_mirrorless_indicators = any(indicator in html_content.lower() 
                                              for indicator in ["mirrorless camera", "full-frame mirrorless", "aps-c mirrorless"])
                
                print(f"  Has 'Digital interchangeable lens, mirrorless camera' spec: {has_mirrorless_spec}")
                print(f"  Has mirrorless indicators: {has_mirrorless_indicators}")
                
                # Check for technical specifications section
                has_tech_spec = 'id="tech-spec-data"' in html_content
                print(f"  Has tech-spec-data section: {has_tech_spec}")
                
                # Count attribution groups (h3 tags)
                h3_count = html_content.count('<h3')
                print(f"  Number of h3 tags (potential attribution groups): {h3_count}")
                
            except Exception as e:
                print(f"  Error analyzing file: {e}")
        else:
            print(f"  File not found: {filename}")


if __name__ == "__main__":
    print("🔍 CANON EOS R FILE ANALYSIS")
    print("=" * 80)
    
    # Analyze all files
    analyze_canon_files()
    
    # Show detailed analysis of specific files
    show_file_details()
    
    print(f"\n✅ Analysis complete!")
    print("\n💡 RECOMMENDATIONS:")
    print("- Use the filtering logic in test_canon_spec_analysis.py")
    print("- Exclude files with 'kit', 'mm', 'creator', 'firmware' in filename")
    print("- Verify mirrorless cameras by checking for 'Digital interchangeable lens, mirrorless camera' specification")
    print("- Use alternative indicators when primary spec is not found")
