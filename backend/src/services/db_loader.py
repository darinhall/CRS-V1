import logging
import json
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseLoader:
    def __init__(self, db_connection):
        self.conn = db_connection

    def upsert_product(self, product_data: Dict[str, Any]) -> str:
        """
        Upserts a product record.
        Returns the product ID (UUID).
        """
        sql = """
            INSERT INTO products (
                brand_id, category_id, model, full_name, slug, 
                source_url, raw_data, last_scraped_at, scraping_status, is_active
            ) VALUES (
                %(brand_id)s, %(category_id)s, %(model)s, %(full_name)s, %(slug)s,
                %(source_url)s, %(raw_data)s, NOW(), 'success', TRUE
            )
            ON CONFLICT (slug) DO UPDATE SET
                full_name = EXCLUDED.full_name,
                raw_data = EXCLUDED.raw_data,
                last_scraped_at = NOW(),
                scraping_status = 'success',
                updated_at = NOW()
            RETURNING id;
        """
        
        try:
            with self.conn.cursor() as cur:
                # Ensure raw_data is json
                if isinstance(product_data.get('raw_data'), dict):
                    product_data['raw_data'] = json.dumps(product_data['raw_data'])
                
                cur.execute(sql, product_data)
                product_id = cur.fetchone()[0]
                self.conn.commit()
                return str(product_id)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to upsert product {product_data.get('slug')}: {e}")
            raise

    def save_specs(self, product_id: str, specs: List[Dict[str, Any]]):
        """
        Saves a list of normalized specs for a product.
        """
        if not specs:
            return

        sql = """
            INSERT INTO product_specs (
                product_id, spec_definition_id, raw_value, 
                spec_value, numeric_value, boolean_value, unit_used
            ) VALUES (
                %(product_id)s, %(spec_definition_id)s, %(raw_value)s,
                %(value_text)s, %(numeric_value)s, %(boolean_value)s, %(unit_used)s
            )
            ON CONFLICT (product_id, spec_definition_id) DO UPDATE SET
                raw_value = EXCLUDED.raw_value,
                spec_value = EXCLUDED.spec_value,
                numeric_value = EXCLUDED.numeric_value,
                boolean_value = EXCLUDED.boolean_value,
                unit_used = EXCLUDED.unit_used,
                scraped_at = NOW();
        """

        try:
            with self.conn.cursor() as cur:
                for spec in specs:
                    spec['product_id'] = product_id
                    cur.execute(sql, spec)
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to save specs for product {product_id}: {e}")
            raise
