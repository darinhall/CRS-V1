-- Seed Brands
INSERT INTO brand (name, slug, website_url, scraping_enabled) VALUES
('Canon', 'canon', 'https://www.usa.canon.com', true),
('Sony', 'sony', 'https://electronics.sony.com', true),
('Nikon', 'nikon', 'https://www.nikonusa.com', true),
('Fujifilm', 'fujifilm', 'https://fujifilm-x.com', true),
('Panasonic', 'panasonic', 'https://shop.panasonic.com', true),
('Blackmagic Design', 'blackmagic-design', 'https://www.blackmagicdesign.com', true),
('Arri', 'arri', 'https://www.arri.com', true),
('RED', 'red', 'https://www.red.com', true),
('DJI', 'dji', 'https://www.dji.com', true),
('GoPro', 'gopro', 'https://gopro.com', true),
('Leica', 'leica', 'https://leica-camera.com', true),
('Sigma', 'sigma', 'https://www.sigmaphoto.com', true),
('Tamron', 'tamron', 'https://www.tamron-usa.com', true),
('Atomos', 'atomos', 'https://www.atomos.com', true),
('SmallHD', 'smallhd', 'https://smallhd.com', true),
('Teradek', 'teradek', 'https://teradek.com', true),
('Wooden Camera', 'wooden-camera', 'https://woodencamera.com', true),
('Tilta', 'tilta', 'https://tilta.com', true),
('Aputure', 'aputure', 'https://www.aputure.com', true),
('Nanlite', 'nanlite', 'https://nanliteus.com', true),
('Godox', 'godox', 'http://www.godox.com', true),
('Profoto', 'profoto', 'https://profoto.com', true),
('Rode', 'rode', 'https://rode.com', true),
('Sennheiser', 'sennheiser', 'https://en-us.sennheiser.com', true),
('Shure', 'shure', 'https://www.shure.com', true),
('Zoom', 'zoom', 'https://zoomcorp.com', true),
('Tascam', 'tascam', 'https://tascam.com', true),
('SanDisk', 'sandisk', 'https://www.westerndigital.com/brand/sandisk', true),
('Lexar', 'lexar', 'https://www.lexar.com', true),
('ProGrade Digital', 'prograde-digital', 'https://progradedigital.com', true),
('Angelbird', 'angelbird', 'https://www.angelbird.com', true),
('Manfrotto', 'manfrotto', 'https://www.manfrotto.com', true),
('Gitzo', 'gitzo', 'https://www.gitzo.com', true),
('Sachtler', 'sachtler', 'https://www.sachtler.com', true),
('Miller', 'miller', 'https://www.millertripods.com', true),
('OConnor', 'oconnor', 'https://www.ocon.com', true),
('Libec', 'libec', 'https://www.libec.co.jp/en', true),
('Benro', 'benro', 'http://www.benro.com', true),
('Sirui', 'sirui', 'https://store.sirui.com', true),
('iFootage', 'ifootage', 'https://www.ifootagegear.com', true),
('Edelkrone', 'edelkrone', 'https://edelkrone.com', true),
('Kessler Crane', 'kessler-crane', 'https://kesslercrane.com', true),
('Matthews Studio Equipment', 'matthews-studio-equipment', 'https://www.msegrip.com', true),
('Avenger', 'avenger', 'https://www.manfrotto.com/us-en/avenger', true),
('Kupo', 'kupo', 'https://kupogrip.com', true),
('Inovativ', 'inovativ', 'https://www.inovativ.com', true),
('Pelican', 'pelican', 'https://www.pelican.com', true),
('Nanuk', 'nanuk', 'https://nanuk.com', true),
('Porta Brace', 'porta-brace', 'https://www.portabrace.com', true),
('Think Tank Photo', 'think-tank-photo', 'https://www.thinktankphoto.com', true),
('Lowepro', 'lowepro', 'https://www.lowepro.com', true),
('Peak Design', 'peak-design', 'https://www.peakdesign.com', true),
('Shimoda Designs', 'shimoda-designs', 'https://shimodadesigns.com', true),
('Wandrd', 'wandrd', 'https://www.wandrd.com', true),
('Moment', 'moment', 'https://www.shopmoment.com', true),
('PolarPro', 'polarpro', 'https://www.polarprofilters.com', true),
('Tiffen', 'tiffen', 'https://tiffen.com', true),
('Schneider', 'schneider', 'https://schneiderkreuznach.com', true),
('Lee Filters', 'lee-filters', 'https://leefilters.com', true),
('Hoya', 'hoya', 'https://hoyafilter.com', true),
('B+W', 'b-w', 'https://schneiderkreuznach.com/en/photo-optics/b-w-filters', true),
('NiSi', 'nisi', 'https://en.nisioptics.com', true),
('K&F Concept', 'k-f-concept', 'https://www.kentfaith.com', true),
('Freewell', 'freewell', 'https://www.freewellgear.com', true),
('Formatt Hitech', 'formatt-hitech', 'https://www.formatt-hitech.com', true),
('Breakthrough Photography', 'breakthrough-photography', 'https://breakthrough.photography', true)
ON CONFLICT (slug) DO NOTHING;

-- Seed Product Categories
-- Root Categories
INSERT INTO product_category (name, slug, display_order, icon_name) VALUES
('Cameras', 'cameras', 10, 'camera'),
('Lenses', 'lenses', 20, 'aperture'),
('Lighting', 'lighting', 30, 'lightbulb'),
('Audio', 'audio', 40, 'mic'),
('Support & Grip', 'support-grip', 50, 'tripod'),
('Drones & Aerial', 'drones-aerial', 60, 'plane'),
('Monitors & Recorders', 'monitors-recorders', 70, 'monitor'),
('Power & Batteries', 'power-batteries', 80, 'battery-charging'),
('Storage & Media', 'storage-media', 90, 'hard-drive'),
('Bags & Cases', 'bags-cases', 100, 'briefcase'),
('Accessories', 'accessories', 110, 'settings')
ON CONFLICT (slug) DO NOTHING;

-- Subcategories: Cameras
DO $$
DECLARE
    parent_id UUID;
BEGIN
    SELECT id INTO parent_id FROM product_category WHERE slug = 'cameras';
    
    INSERT INTO product_category (name, slug, parent_category_id, display_order) VALUES
    ('Mirrorless Cameras', 'mirrorless-cameras', parent_id, 10),
    ('DSLR Cameras', 'dslr-cameras', parent_id, 20),
    ('Cinema Cameras', 'cinema-cameras', parent_id, 30),
    ('Action Cameras', 'action-cameras', parent_id, 40),
    ('Camcorders', 'camcorders', parent_id, 50),
    ('Compact Cameras', 'compact-cameras', parent_id, 60),
    ('Medium Format Cameras', 'medium-format-cameras', parent_id, 70),
    ('Film Cameras', 'film-cameras', parent_id, 80),
    ('360 Cameras', '360-cameras', parent_id, 90)
    ON CONFLICT (slug) DO NOTHING;
END $$;

-- Subcategories: Lenses
DO $$
DECLARE
    parent_id UUID;
BEGIN
    SELECT id INTO parent_id FROM product_category WHERE slug = 'lenses';
    
    INSERT INTO product_category (name, slug, parent_category_id, display_order) VALUES
    ('Mirrorless Lenses', 'mirrorless-lenses', parent_id, 10),
    ('DSLR Lenses', 'dslr-lenses', parent_id, 20),
    ('Cinema Lenses', 'cinema-lenses', parent_id, 30),
    ('Rangefinder Lenses', 'rangefinder-lenses', parent_id, 40),
    ('Lens Adapters', 'lens-adapters', parent_id, 50),
    ('Teleconverters', 'teleconverters', parent_id, 60),
    ('Lens Filters', 'lens-filters', parent_id, 70)
    ON CONFLICT (slug) DO NOTHING;
END $$;

-- ------------------------------------------------------------
-- Canon EOS R6 Mark III (structure skeleton / clean seed)
-- Source: https://www.usa.canon.com/shop/p/eos-r6-mark-iii
-- Values aligned to Canon-published specs (Canon USA).
-- ------------------------------------------------------------

-- Seed Spec Sections + Definitions (Mirrorless Cameras)
DO $$
DECLARE
    cat_id UUID;
    mount_section UUID;
    sensor_section UUID;
    recording_section UUID;
    lens_section UUID;
    exposure_section UUID;
    connectivity_section UUID;
    physical_section UUID;
    power_section UUID;
    general_section UUID;
    display_section UUID;
    shutter_section UUID;
    storage_section UUID;
BEGIN
    SELECT id INTO cat_id FROM product_category WHERE slug = 'mirrorless-cameras';

    -- Sections
    -- "General" section for overall camera classification
    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('General', cat_id, 5)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO general_section FROM spec_section WHERE section_name = 'General' AND category_id = cat_id;

    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('Mount', cat_id, 10)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO mount_section FROM spec_section WHERE section_name = 'Mount' AND category_id = cat_id;

    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('Image Sensor', cat_id, 20)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO sensor_section FROM spec_section WHERE section_name = 'Image Sensor' AND category_id = cat_id;

    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('Recording', cat_id, 30)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO recording_section FROM spec_section WHERE section_name = 'Recording' AND category_id = cat_id;

    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('Lens Compatibility', cat_id, 40)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO lens_section FROM spec_section WHERE section_name = 'Lens Compatibility' AND category_id = cat_id;

    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('Exposure', cat_id, 50)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO exposure_section FROM spec_section WHERE section_name = 'Exposure' AND category_id = cat_id;

    -- Shutter section (separates shutter-speed-related specs from general exposure)
    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('Shutter', cat_id, 55)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO shutter_section FROM spec_section WHERE section_name = 'Shutter' AND category_id = cat_id;

    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('Connectivity', cat_id, 60)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO connectivity_section FROM spec_section WHERE section_name = 'Connectivity' AND category_id = cat_id;

    -- Storage section (cards/media)
    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('Storage', cat_id, 65)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO storage_section FROM spec_section WHERE section_name = 'Storage' AND category_id = cat_id;

    -- Display section (LCD/EVF/etc.)
    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('Display', cat_id, 68)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO display_section FROM spec_section WHERE section_name = 'Display' AND category_id = cat_id;

    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('Physical', cat_id, 70)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO physical_section FROM spec_section WHERE section_name = 'Physical' AND category_id = cat_id;

    INSERT INTO spec_section (section_name, category_id, display_order)
    VALUES ('Power', cat_id, 80)
    ON CONFLICT (section_name, category_id) DO NOTHING;
    SELECT id INTO power_section FROM spec_section WHERE section_name = 'Power' AND category_id = cat_id;

    -- Definitions (normalized taxonomy)
    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (mount_section, 'Lens Mount', 'lens_mount', 'text', NULL, cat_id, 10)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (sensor_section, 'Effective Pixels', 'effective_pixels', 'number', 'MP', cat_id, 10)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (recording_section, 'Recording Format', 'recording_format', 'text', NULL, cat_id, 8)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (lens_section, 'Compatible Lenses', 'compatible_lenses', 'text', NULL, cat_id, 8)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (exposure_section, 'Exposure Compensation', 'exposure_compensation', 'text', NULL, cat_id, 7)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (connectivity_section, 'Transmission Method', 'transmission_method', 'text', NULL, cat_id, 6)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (physical_section, 'Dimensions', 'dimensions', 'text', NULL, cat_id, 6)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (physical_section, 'Weight', 'weight', 'number', 'g', cat_id, 6)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (power_section, 'Battery', 'battery', 'text', NULL, cat_id, 7)
    ON CONFLICT (normalized_key) DO NOTHING;

    -- Additional definitions requested for EOS R6 Mark III seed (grouped into a uniform taxonomy)
    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (general_section, 'Body Type', 'body_type', 'text', NULL, cat_id, 5)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (sensor_section, 'Max Resolution', 'max_resolution', 'text', NULL, cat_id, 6)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (sensor_section, 'Sensor Size', 'sensor_size', 'text', NULL, cat_id, 8)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (sensor_section, 'Sensor Type', 'sensor_type', 'text', NULL, cat_id, 8)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (exposure_section, 'ISO', 'iso', 'range', 'ISO', cat_id, 8)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (sensor_section, 'Focal Length Multiplier', 'focal_length_multiplier', 'number', 'x', cat_id, 5)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (display_section, 'Articulated LCD', 'articulated_lcd', 'boolean', NULL, cat_id, 5)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (display_section, 'Screen Size', 'screen_size', 'number', 'in', cat_id, 5)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (display_section, 'Screen Dots', 'screen_dots', 'number', 'dots', cat_id, 4)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (shutter_section, 'Max Shutter Speed', 'max_shutter_speed', 'text', NULL, cat_id, 6)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (sensor_section, 'Format', 'format', 'text', NULL, cat_id, 6)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (storage_section, 'Storage Types', 'storage_types', 'list', NULL, cat_id, 6)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (connectivity_section, 'USB', 'usb', 'text', NULL, cat_id, 5)
    ON CONFLICT (normalized_key) DO NOTHING;

    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (connectivity_section, 'GPS', 'gps', 'boolean', NULL, cat_id, 4)
    ON CONFLICT (normalized_key) DO NOTHING;

    -- Table/Matrix spec example (from Canon PDF): Still image recording -> recording pixels
    INSERT INTO spec_definition (section_id, display_name, normalized_key, data_type, unit, category_id, importance)
    VALUES (recording_section, 'Still Image Recording Pixels (Matrix)', 'still_image_recording_pixels', 'matrix', NULL, cat_id, 6)
    ON CONFLICT (normalized_key) DO NOTHING;

    -- If seed is re-run on an existing DB, enforce section placement for these keys.
    UPDATE spec_definition
    SET section_id = general_section
    WHERE normalized_key = 'body_type';

    UPDATE spec_definition
    SET section_id = display_section
    WHERE normalized_key IN ('articulated_lcd', 'screen_size', 'screen_dots');

    UPDATE spec_definition
    SET section_id = shutter_section
    WHERE normalized_key = 'max_shutter_speed';

    UPDATE spec_definition
    SET section_id = storage_section
    WHERE normalized_key = 'storage_types';
END $$;

-- Seed Product + Spec Values (EOS R6 Mark III)
DO $$
DECLARE
    v_canon_id UUID;
    v_cat_id UUID;
    v_product_id UUID;
BEGIN
    SELECT id INTO v_canon_id FROM brand WHERE slug = 'canon';
    SELECT id INTO v_cat_id FROM product_category WHERE slug = 'mirrorless-cameras';

    INSERT INTO product (
        brand_id,
        category_id,
        model,
        full_name,
        slug,
        manufacturer_url,
        source_url,
        scraping_status
    ) VALUES (
        v_canon_id,
        v_cat_id,
        'EOS R6 Mark III',
        'Canon EOS R6 Mark III',
        'eos-r6-mark-iii',
        'https://www.usa.canon.com/shop/p/eos-r6-mark-iii',
        'https://www.usa.canon.com/shop/p/eos-r6-mark-iii',
        'seeded'
    )
    ON CONFLICT (slug) DO NOTHING;

    SELECT id INTO v_product_id FROM product WHERE slug = 'eos-r6-mark-iii';

    -- Lens mount
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT v_product_id, sd.id, 'Canon RF', 'Canon RF', 1.0
    FROM spec_definition sd
    JOIN spec_section ss ON ss.id = sd.section_id
    WHERE sd.normalized_key = 'lens_mount'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Effective pixels
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, numeric_value, unit_used, extraction_confidence)
    SELECT v_product_id, sd.id, 'Approx. 32.5 MP', 'Approx. 32.5 million pixels', 32.5, 'MP', 1.0
    FROM spec_definition sd
    JOIN spec_section ss ON ss.id = sd.section_id
    WHERE sd.normalized_key = 'effective_pixels'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Recording format
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT
        v_product_id,
        sd.id,
        'Still: RAW (Canon RAW/C-RAW), JPEG, HEIF; Movie: RAW, XF-HEVC S (H.265/HEVC), XF-AVC S (H.264/MPEG-4 AVC)',
        'Still: RAW (Canon RAW/C-RAW), JPEG, HEIF; Movie: RAW, XF-HEVC S (H.265/HEVC), XF-AVC S (H.264/MPEG-4 AVC)',
        1.0
    FROM spec_definition sd
    JOIN spec_section ss ON ss.id = sd.section_id
    WHERE sd.normalized_key = 'recording_format'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Compatible lenses
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT
        v_product_id,
        sd.id,
        'Canon RF and RF-S lenses; via Mount Adapter EF-EOS R: EF, EF-S, TS-E, and MP-E lenses',
        'Canon RF and RF-S lenses; via Mount Adapter EF-EOS R: EF, EF-S, TS-E, and MP-E lenses',
        1.0
    FROM spec_definition sd
    JOIN spec_section ss ON ss.id = sd.section_id
    WHERE sd.normalized_key = 'compatible_lenses'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Exposure compensation
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT
        v_product_id,
        sd.id,
        '±3 stops (1/3- or 1/2-stop increments)',
        '±3 stops (1/3- or 1/2-stop increments)',
        1.0
    FROM spec_definition sd
    JOIN spec_section ss ON ss.id = sd.section_id
    WHERE sd.normalized_key = 'exposure_compensation'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Transmission method
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT
        v_product_id,
        sd.id,
        'Wi-Fi (IEEE 802.11ac), Bluetooth 5.1',
        'Wi-Fi (IEEE 802.11ac), Bluetooth 5.1',
        1.0
    FROM spec_definition sd
    JOIN spec_section ss ON ss.id = sd.section_id
    WHERE sd.normalized_key = 'transmission_method'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Dimensions
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT
        v_product_id,
        sd.id,
        'Approx. 138.4 x 98.4 x 88.4 mm (5.45 x 3.87 x 3.48 in)',
        'Approx. 138.4 x 98.4 x 88.4 mm (5.45 x 3.87 x 3.48 in)',
        1.0
    FROM spec_definition sd
    JOIN spec_section ss ON ss.id = sd.section_id
    WHERE sd.normalized_key = 'dimensions'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Weight
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, numeric_value, unit_used, extraction_confidence)
    SELECT
        v_product_id,
        sd.id,
        'Approx. 699 g (24.66 oz) incl. battery and one card',
        'Approx. 699 g (24.66 oz) incl. battery and one card',
        699,
        'g',
        1.0
    FROM spec_definition sd
    JOIN spec_section ss ON ss.id = sd.section_id
    WHERE sd.normalized_key = 'weight'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Battery
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT
        v_product_id,
        sd.id,
        'LP-E6P (compatible with LP-E6NH and LP-E6N with limitations)',
        'LP-E6P (compatible with LP-E6NH and LP-E6N with limitations)',
        1.0
    FROM spec_definition sd
    JOIN spec_section ss ON ss.id = sd.section_id
    WHERE sd.normalized_key = 'battery'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Additional requested specs (skip ones already seeded above like lens_mount/weight/dimensions/etc.)

    -- Body type
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT v_product_id, sd.id,
        'Full-frame mirrorless (interchangeable lens)',
        'Full-frame mirrorless camera (RF mount)',
        0.95
    FROM spec_definition sd
    WHERE sd.normalized_key = 'body_type'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Max resolution (Canon-published Open Gate resolution; note: video spec)
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT v_product_id, sd.id,
        '6960 x 4640 (Open Gate, 3:2)',
        'Open Gate recording: 6960 x 4640 (3:2)',
        0.95
    FROM spec_definition sd
    WHERE sd.normalized_key = 'max_resolution'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Sensor size
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT v_product_id, sd.id,
        'Full-frame (approx. 36 x 24 mm)',
        'Full-frame (approx. 36 x 24 mm)',
        0.95
    FROM spec_definition sd
    WHERE sd.normalized_key = 'sensor_size'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Sensor type
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT v_product_id, sd.id,
        'CMOS',
        'Full-frame CMOS',
        0.95
    FROM spec_definition sd
    WHERE sd.normalized_key = 'sensor_type'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- ISO
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, min_value, max_value, unit_used, extraction_confidence)
    SELECT v_product_id, sd.id,
        'Still: ISO 100–64000 (expandable 50–102400); Movie: ISO 100–25600 (expandable up to 102400)',
        'Still: ISO 100–64000 (expandable 50–102400); Movie: ISO 100–25600 (expandable up to 102400)',
        100, 64000, 'ISO',
        0.95
    FROM spec_definition sd
    WHERE sd.normalized_key = 'iso'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Focal length multiplier
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, numeric_value, unit_used, extraction_confidence)
    SELECT v_product_id, sd.id,
        '1.0x',
        '1.0x (full-frame)',
        1.0, 'x',
        0.90
    FROM spec_definition sd
    WHERE sd.normalized_key = 'focal_length_multiplier'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Articulated LCD
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, boolean_value, extraction_confidence)
    SELECT v_product_id, sd.id,
        'Yes (vari-angle)',
        'Vari-angle LCD touchscreen',
        TRUE,
        0.95
    FROM spec_definition sd
    WHERE sd.normalized_key = 'articulated_lcd'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Screen size
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, numeric_value, unit_used, extraction_confidence)
    SELECT v_product_id, sd.id,
        '3.0 in',
        '3.0-inch vari-angle LCD',
        3.0, 'in',
        0.95
    FROM spec_definition sd
    WHERE sd.normalized_key = 'screen_size'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Screen dots
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, numeric_value, unit_used, extraction_confidence)
    SELECT v_product_id, sd.id,
        'Approx. 1.62 million dots',
        'Approx. 1.62 million dots',
        1620000, 'dots',
        0.95
    FROM spec_definition sd
    WHERE sd.normalized_key = 'screen_dots'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Max shutter speed
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT v_product_id, sd.id,
        'Up to 1/8000s (mechanical), up to 1/16000s (electronic)',
        'Still: up to 1/8000 (mechanical), up to 1/16000 (electronic)',
        0.90
    FROM spec_definition sd
    WHERE sd.normalized_key = 'max_shutter_speed'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Format
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT v_product_id, sd.id,
        'Full-frame',
        'Full-frame',
        0.95
    FROM spec_definition sd
    WHERE sd.normalized_key = 'format'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Storage types
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT v_product_id, sd.id,
        '1x CFexpress Type B; 1x SD/SDHC/SDXC (UHS-II)',
        'Dual card slots: CFexpress Type B + UHS-II SD',
        0.95
    FROM spec_definition sd
    WHERE sd.normalized_key = 'storage_types'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- USB
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, extraction_confidence)
    SELECT v_product_id, sd.id,
        'USB-C (USB 3.2 Gen 2), USB Power Delivery (charging)',
        'USB-C terminal supports USB 3.2 Gen 2; supports USB PD charging',
        0.95
    FROM spec_definition sd
    WHERE sd.normalized_key = 'usb'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- GPS
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, boolean_value, extraction_confidence)
    SELECT v_product_id, sd.id,
        'No (use smartphone GPS via Canon Camera Connect)',
        'No built-in GPS; geotag via Canon Camera Connect',
        FALSE,
        0.90
    FROM spec_definition sd
    WHERE sd.normalized_key = 'gps'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Still image recording pixels (matrix lives in product_spec_matrix; keep a parent product_spec row for discovery)
    INSERT INTO product_spec (product_id, spec_definition_id, spec_value, raw_value, raw_value_jsonb, extraction_confidence)
    SELECT v_product_id, sd.id,
        'See product_spec_matrix (still image recording pixels)',
        'PDF table: Recording pixels — cropping & aspect ratios (values approximate; rounded; shaded cells inexact proportion)',
        '{
          "source": "canon_pdf",
          "table": "Recording pixels — cropping & aspect ratios",
          "scope": "Still image recording",
          "notes": [
            "Values for recorded pixels rounded off to nearest 100,000th",
            "Shaded cells indicate inexact proportion",
            "RAW and C-RAW images generated in 3:2 aspect ratio; set aspect ratio/cropping is appended and applied in RAW processing",
            "JPEG/HEIF images generated in the set aspect ratio",
            "These aspect ratios and pixel counts also apply to resizing"
          ],
          "dims": ["media_type", "image_size", "aspect_ratio"],
          "value_fields": ["numeric_value_mp", "width_px", "height_px", "is_available", "is_inexact_proportion"]
        }'::jsonb,
        1.0
    FROM spec_definition sd
    WHERE sd.normalized_key = 'still_image_recording_pixels'
    ON CONFLICT (product_id, spec_definition_id) DO NOTHING;

    -- Matrix cells (EOS R6 Mark III) -> product_spec_matrix
    INSERT INTO product_spec_matrix (
        product_id,
        spec_definition_id,
        dims,
        numeric_value,
        unit_used,
        width_px,
        height_px,
        is_available,
        is_inexact_proportion,
        notes,
        extraction_confidence
    )
    SELECT
        v_product_id,
        sd.id,
        v.dims::jsonb,
        v.mp,
        'MP',
        v.w,
        v.h,
        v.is_available,
        v.is_inexact,
        v.notes,
        1.0
    FROM spec_definition sd
    CROSS JOIN (
        VALUES
          -- JPEG/HEIF - L
          ('{"media_type":"JPEG/HEIF","image_size":"L","aspect_ratio":"3:2"}',      32.3::numeric, 6960::int, 4640::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"L","aspect_ratio":"1.6x_crop"}',12.4::numeric, 4320::int, 2880::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"L","aspect_ratio":"1:1"}',      21.5::numeric, 4640::int, 4640::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"L","aspect_ratio":"4:3"}',      28.6::numeric, 6160::int, 4640::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"L","aspect_ratio":"16:9"}',     27.2::numeric, 6960::int, 3904::int, true,  false, NULL),

          -- JPEG/HEIF - M
          ('{"media_type":"JPEG/HEIF","image_size":"M","aspect_ratio":"3:2"}',      15.4::numeric, 4800::int, 3200::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"M","aspect_ratio":"1.6x_crop"}',NULL::numeric, NULL::int, NULL::int, false, false, 'Not available'),
          ('{"media_type":"JPEG/HEIF","image_size":"M","aspect_ratio":"1:1"}',      10.2::numeric, 3200::int, 3200::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"M","aspect_ratio":"4:3"}',      13.6::numeric, 4256::int, 3200::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"M","aspect_ratio":"16:9"}',     12.9::numeric, 4880::int, 2688::int, true,  false, NULL),

          -- JPEG/HEIF - S1 (3:2 cell shaded in PDF = inexact proportion)
          ('{"media_type":"JPEG/HEIF","image_size":"S1","aspect_ratio":"3:2"}',      8.1::numeric, 3472::int, 2320::int, true,  true,  NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"S1","aspect_ratio":"1.6x_crop"}',NULL::numeric, NULL::int, NULL::int, false, false, 'Not available'),
          ('{"media_type":"JPEG/HEIF","image_size":"S1","aspect_ratio":"1:1"}',      5.4::numeric, 2320::int, 2320::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"S1","aspect_ratio":"4:3"}',      7.1::numeric, 3072::int, 2320::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"S1","aspect_ratio":"16:9"}',     6.8::numeric, 3472::int, 1952::int, true,  false, NULL),

          -- JPEG/HEIF - S2 (some cells shaded in PDF = inexact proportion)
          ('{"media_type":"JPEG/HEIF","image_size":"S2","aspect_ratio":"3:2"}',      3.8::numeric, 2400::int, 1600::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"S2","aspect_ratio":"1.6x_crop"}',3.8::numeric, 2400::int, 1600::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"S2","aspect_ratio":"1:1"}',      2.6::numeric, 1600::int, 1600::int, true,  false, NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"S2","aspect_ratio":"4:3"}',      3.4::numeric, 2112::int, 1600::int, true,  true,  NULL),
          ('{"media_type":"JPEG/HEIF","image_size":"S2","aspect_ratio":"16:9"}',     3.2::numeric, 2400::int, 1344::int, true,  true,  NULL),

          -- RAW / C-RAW
          ('{"media_type":"RAW/C-RAW","image_size":"RAW/C-RAW","aspect_ratio":"3:2"}',      32.3::numeric, 6960::int, 4640::int, true,  false, NULL),
          ('{"media_type":"RAW/C-RAW","image_size":"RAW/C-RAW","aspect_ratio":"1.6x_crop"}',12.4::numeric, 4320::int, 2880::int, true,  false, NULL),
          ('{"media_type":"RAW/C-RAW","image_size":"RAW/C-RAW","aspect_ratio":"4:3"}',      32.3::numeric, 6960::int, 4640::int, true,  false, NULL)
    ) AS v(dims, mp, w, h, is_available, is_inexact, notes)
    WHERE sd.normalized_key = 'still_image_recording_pixels'
    ON CONFLICT (product_id, spec_definition_id, dims) DO NOTHING;
END $$;
