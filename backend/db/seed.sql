-- Seed Brands
INSERT INTO brands (name, slug, website_url, scraping_enabled) VALUES
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
INSERT INTO product_categories (name, slug, display_order, icon_name) VALUES
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
    SELECT id INTO parent_id FROM product_categories WHERE slug = 'cameras';
    
    INSERT INTO product_categories (name, slug, parent_category_id, display_order) VALUES
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
    SELECT id INTO parent_id FROM product_categories WHERE slug = 'lenses';
    
    INSERT INTO product_categories (name, slug, parent_category_id, display_order) VALUES
    ('Mirrorless Lenses', 'mirrorless-lenses', parent_id, 10),
    ('DSLR Lenses', 'dslr-lenses', parent_id, 20),
    ('Cinema Lenses', 'cinema-lenses', parent_id, 30),
    ('Rangefinder Lenses', 'rangefinder-lenses', parent_id, 40),
    ('Lens Adapters', 'lens-adapters', parent_id, 50),
    ('Teleconverters', 'teleconverters', parent_id, 60),
    ('Lens Filters', 'lens-filters', parent_id, 70)
    ON CONFLICT (slug) DO NOTHING;
END $$;
