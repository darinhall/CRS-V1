import os
import sys
import logging
import psycopg2
from dotenv import load_dotenv

# Add backend to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.discovery_agent import DiscoveryAgent
from src.agents.extraction_agent import ExtractionAgent
from src.services.spec_mapper import SpecMapperService
from src.services.db_loader import DatabaseLoader

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Explicitly load .env from backend/ directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_path)
    
    # DB Connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL not set in environment.")
        logger.error(f"Please create a .env file at {env_path}")
        logger.error("You can copy backend/env_example.txt to start.")
        return

    try:
        conn = psycopg2.connect(db_url)
        logger.info("Connected to Database")
    except Exception as e:
        logger.error(f"Failed to connect to DB: {e}")
        return

    # Initialize Services
    mapper = SpecMapperService(conn)
    loader = DatabaseLoader(conn)
    
    # Initialize Agents
    discovery = DiscoveryAgent(headless=False) # Visual debug
    extraction = ExtractionAgent(headless=False)

    # 1. Discovery Phase
    brand_url = "https://www.usa.canon.com/shop/cameras/mirrorless-cameras"
    product_pattern = "/shop/p/"
    
    logger.info("Starting Discovery Phase...")
    # For testing, we might want to limit this or check if we already have URLs
    product_urls = discovery.discover_products(brand_url, product_pattern)
    logger.info(f"Discovered {len(product_urls)} products")

    # 2. Extraction & Loading Phase
    # Get Brand ID and Category ID (Hardcoded for this test script, but should be dynamic)
    # In a real run, we'd query these based on input
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM brands WHERE slug = 'canon'")
            brand_id = cur.fetchone()[0]
            cur.execute("SELECT id FROM product_categories WHERE slug = 'mirrorless-cameras'")
            category_id = cur.fetchone()[0]
    except Exception as e:
        logger.error("Could not find Brand/Category IDs. Did you run the seed script?")
        conn.close()
        return

    for i, url in enumerate(product_urls):
        logger.info(f"Processing ({i+1}/{len(product_urls)}): {url}")
        
        # Extract
        data = extraction.extract_specs(url)
        if "error" in data:
            logger.error(f"Skipping {url} due to extraction error")
            continue

        raw_specs = data.get("specs", {})
        
        # Prepare Product Data
        product_slug = url.split("/")[-1].replace(".html", "")
        product_data = {
            "brand_id": brand_id,
            "category_id": category_id,
            "model": product_slug.replace("-", " ").title(), # Simple heuristic
            "full_name": product_slug.replace("-", " ").title(),
            "slug": product_slug,
            "source_url": url,
            "raw_data": data # Store full dump
        }
        
        # Upsert Product
        try:
            product_id = loader.upsert_product(product_data)
            
            # Normalize & Upsert Specs
            normalized_specs = []
            for group, attrs in raw_specs.items():
                for key, val in attrs.items():
                    # Map Spec
                    mapped = mapper.map_spec(key, context=group, raw_value=val)
                    if mapped:
                        mapped["raw_value"] = val
                        normalized_specs.append(mapped)
                    else:
                        # Optional: Log unmapped specs for future rule improvement
                        pass
            
            loader.save_specs(product_id, normalized_specs)
            logger.info(f"Saved product {product_slug} with {len(normalized_specs)} specs")
            
        except Exception as e:
            logger.error(f"Failed to save product {product_slug}: {e}")

    conn.close()
    logger.info("Pipeline Run Complete")

if __name__ == "__main__":
    main()
