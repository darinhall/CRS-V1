-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Brands Table
CREATE TABLE IF NOT EXISTS brands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    website_url TEXT,
    logo_url TEXT,
    scraping_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Product Categories Table
CREATE TABLE IF NOT EXISTS product_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    parent_category_id UUID REFERENCES product_categories(id),
    display_order INTEGER DEFAULT 0,
    icon_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Spec Sections (Groups like "Image Sensor", "Focus")
CREATE TABLE IF NOT EXISTS spec_sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_name TEXT NOT NULL,
    category_id UUID REFERENCES product_categories(id), -- Optional link to category
    display_order INTEGER DEFAULT 0,
    parent_section_id UUID REFERENCES spec_sections(id),
    UNIQUE(section_name, category_id)
);

-- Spec Definitions (Master taxonomy like "Effective Pixels")
CREATE TABLE IF NOT EXISTS spec_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_id UUID REFERENCES spec_sections(id),
    display_name TEXT NOT NULL, -- The canonical name
    normalized_key TEXT NOT NULL UNIQUE, -- For programmatic access (e.g., effective_pixels)
    data_type TEXT DEFAULT 'text', -- 'text', 'number', 'boolean', 'range', 'list'
    unit TEXT, -- Default unit (e.g. 'MP', 'mm', 'g')
    category_id UUID REFERENCES product_categories(id), -- Optional: restrict spec to category
    description TEXT,
    importance INTEGER DEFAULT 0 -- For sorting/highlighting (0-10)
);

-- Spec Mappings (Translation layer)
CREATE TABLE IF NOT EXISTS spec_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    spec_definition_id UUID REFERENCES spec_definitions(id) NOT NULL,
    extraction_pattern TEXT NOT NULL, -- Regex or string match
    context_pattern TEXT, -- Regex for section context (e.g. "Focus")
    manufacturer_key TEXT, -- If specific to a brand (e.g. Canon calls it X)
    priority INTEGER DEFAULT 0, -- Higher wins
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID REFERENCES brands(id) NOT NULL,
    category_id UUID REFERENCES product_categories(id) NOT NULL,
    model TEXT NOT NULL,
    full_name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    sku TEXT,
    upc TEXT,
    release_date DATE,
    discontinued_date DATE,
    msrp_usd NUMERIC(10, 2),
    current_price_usd NUMERIC(10, 2),
    primary_image_url TEXT,
    thumbnail_url TEXT,
    manufacturer_url TEXT,
    
    -- Scraping Metadata
    source_url TEXT,
    raw_data JSONB, -- Full scrape dump
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    scraping_status TEXT DEFAULT 'pending', -- pending, success, failed
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Product Specs (Normalized Data)
CREATE TABLE IF NOT EXISTS product_specs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE NOT NULL,
    spec_definition_id UUID REFERENCES spec_definitions(id) NOT NULL,
    
    -- Values
    spec_value TEXT, -- The cleaned text value
    raw_value TEXT, -- The original extracted string
    
    -- Structured Values for Filtering
    numeric_value NUMERIC,
    min_value NUMERIC,
    max_value NUMERIC,
    unit_used TEXT,
    boolean_value BOOLEAN,
    
    spec_key TEXT, -- Denormalized key for easier querying if needed
    spec_section TEXT, -- Denormalized section
    
    extraction_confidence FLOAT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(product_id, spec_definition_id)
);

-- Indexes
CREATE INDEX idx_products_brand ON products(brand_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_raw_data ON products USING GIN (raw_data);

CREATE INDEX idx_product_specs_product ON product_specs(product_id);
CREATE INDEX idx_product_specs_definition ON product_specs(spec_definition_id);
CREATE INDEX idx_product_specs_numeric ON product_specs(numeric_value);
CREATE INDEX idx_spec_mappings_pattern ON spec_mappings(extraction_pattern);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();
