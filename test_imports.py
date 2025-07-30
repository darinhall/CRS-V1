#!/usr/bin/env python3
"""
Test script to verify all imports work correctly for canon_scraper.py
"""

def test_imports():
    """Test all required imports"""
    try:
        print("Testing imports...")
        
        # Test requests
        import requests
        print("✅ requests imported successfully")
        
        # Test BeautifulSoup
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup imported successfully")
        
        # Test pandas
        import pandas as pd
        print("✅ pandas imported successfully")
        
        # Test playwright
        from playwright.sync_api import sync_playwright
        print("✅ playwright.sync_api imported successfully")
        
        # Test other imports used in canon_scraper.py
        import json
        import time
        from urllib.parse import urljoin, urlparse
        import re
        from pathlib import Path
        import xml.etree.ElementTree as ET
        print("✅ All standard library imports work")
        
        print("\n🎉 All imports successful! Your environment is ready.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_imports() 