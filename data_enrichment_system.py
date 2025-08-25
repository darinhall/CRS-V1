#!/usr/bin/env python3
"""
Canon Data Enrichment System

This system provides a safe, structured way to fill missing attributes in the comprehensive
Canon mirrorless camera data with minimal risk of JSON structure errors.
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
import html

class CanonDataEnrichment:
    """Safe data enrichment system for Canon camera specifications."""
    
    def __init__(self):
        self.input_file = Path("data/company_product/canon/processed_data/schema/body_mirrorless2.json")
        self.output_file = Path("data/company_product/canon/processed_data/schema/body_mirrorless2_enriched.json")
        self.backup_file = Path("data/company_product/canon/processed_data/schema/body_mirrorless2_backup.json")
        
        # Load reference data sources
        self.reference_data = self.load_reference_data()
        
    def load_reference_data(self):
        """Load reference data from various sources."""
        reference = {
            'common_values': {},
            'camera_specific': {},
            'defaults': {}
        }
        
        # Common values that appear across multiple cameras
        reference['common_values'] = {
            'type_type_type': 'Digital single-lens non-reflex AF/AE camera',
            'type_image_processor': 'DIGIC X',
            'type_lens_mount': 'Canon RF mount',
            'type_image_sensor_type': 'Canon designed full-frame back-illuminated stacked CMOS sensor (compatible with Dual Pixel CMOS AF and Cross-type AF)',
            'type_viewfinder_type': 'OLED color electronic viewfinder; 0.5-inch, approx. 9.44 million dots',
            'type_shutter_type': 'Electronically controlled focal-plane shutter(1) Electronic first curtain(2) Mechanical shutter(3) Electronic shutter',
            'type_lcd_screen_type': 'TFT color, liquid-crystal monitor',
            'type_autofocus_cross_type_af': 'Supported* Dual Pixel CMOS AF has been vertical-line detection only with previous models, but the EOS R1 can perform not only vertical-line detection but also horizontal-line detection by rotating the pupil division direction of the Gb pixels of the CMOS sensor by 90 degrees',
            'color_filter_system': 'RGB primary color filters',
            'low_pass_filter': 'Installed in front of the image sensor, non-detachable',
            'recording_format': 'Compliant to Design rule for Camera File system 2.0 and Exif 2.3',
            'color_space': 'Selectable between sRGB and Adobe RGB',
            'viewfinder': 'OLED color electronic viewfinder',
            'focus_method': 'One-Shot AF, Servo AF, Manual (Manual focus)',
            'white_balance': 'Auto (Ambience priority/White priority), Daylight, Shade, Cloudy, Tungsten light, White fluorescent light, Flash, Custom (Custom WB), Color temperature',
            'auto_white_balance': 'Option between ambience priority and white priority settings',
            'white_balance_shift': 'Blue/amber bias: ±9 levels, Magenta/green bias: ±9 levels',
            'coverage': 'Approx. 100% vertically and horizontally relative to the shooting image area',
            'magnification_or_angle_of_view': 'Approx. 0.70 (with 50mm lens at infinity, -1 m-1)',
            'eye_point': 'Approx. 22mm (at -1 m-1 from the eyepiece lens end)',
            'dioptric_adjustment_range': 'Approx. -4.0 to + 2.0 m-1 (dpt)',
            'aspect_ratio': '3:2 (Horizontal:Vertical)',
            'dust_deletion_feature': 'Self Cleaning Sensor Unit, Removes dust adhering to the low-pass filter',
            'file_numbering': 'File numbering methods: Continuous numbering, Auto reset, Manual reset',
            'raw_plus_jpeg_or_heif_simultaneous_recording': 'Possible'
        }
        
        # Camera-specific values (model-dependent)
        reference['camera_specific'] = {
            'EOS R1': {
                'type_type_type': 'Digital interchangeable lens, mirrorless camera',
                'type_image_processor': 'DIGIC X (with DIGIC Accelerator co-processor)',
                'type_recording_media': '(Two) CFexpress Type B card slots• compatible with CFexpress 2.0 and VPG400',
                'type_compatible_lenses': 'Canon RF lens group (including RF-S lenses)When using Mount Adapter EF-EOS R: Canon EF or EF-S lenses (excluding EF-M lenses)',
                'type_lens_mount': 'Canon RF mount',
                'type_image_sensor_type': 'Canon designed full-frame back-illuminated stacked CMOS sensor (compatible with Dual Pixel CMOS AF and Cross-type AF)',
                'type_viewfinder_type': 'OLED color electronic viewfinder; 0.5-inch, approx. 9.44 million dots',
                'type_autofocus_cross_type_af': 'Supported* Dual Pixel CMOS AF has been vertical-line detection only with previous models, but the EOS R1 can perform not only vertical-line detection but also horizontal-line detection by rotating the pupil division direction of the Gb pixels of the CMOS sensor by 90 degrees',
                'type_shutter_type': 'Electronically controlled focal-plane shutter(1) Electronic first curtain(2) Mechanical shutter(3) Electronic shutter',
                'type_lcd_screen_type': 'TFT color, liquid-crystal monitor',
                'effective_pixels': 'Approx. 24.0 megapixels',
                'total_pixels': 'Approx. 27.1 megapixels',
                'screen_size': '3.0-inch (screen aspect ratio of 3:2)',
                'pixel_unit': 'Approx. 4.40 micro square',
                'weight': 'Approx. 1,010g (including battery and memory card)',
                'dimensions_w_x_h_x_d': 'Approx. 158.4 × 165.7 × 87.8mm'
            },
            'EOS R3': {
                'type_type_type': 'Digital interchangeable lens, mirrorless camera',
                'type_image_processor': 'DIGIC X',
                'type_recording_media': 'SD/SDHC/SDXC memory cards',
                'type_compatible_lenses': 'Canon RF lens group (excluding EF, EF-S and EF-M lenses)When using Mount Adapter EF-EOS R: Canon EF or EF-S lenses (excluding EF-M lenses)',
                'type_lens_mount': 'Canon RF mount',
                'type_image_sensor_type': 'CMOS sensor (compatible with Dual Pixel CMOS AF)',
                'type_viewfinder_type': 'OLED color electronic viewfinder',
                'type_shutter_type': 'Electronically controlled focal-plane shutter',
                'type_lcd_screen_type': 'TFT color, liquid-crystal monitor',
                'effective_pixels': 'Approx. 24.1 megapixels',
                'total_pixels': 'Approx. 25.5 megapixels',
                'screen_size': '3.2-inch (screen aspect ratio of 3:2)',
                'pixel_unit': 'Approx. 6.0 micro square',
                'weight': 'Approx. 1,015g (including battery and memory card)',
                'dimensions_w_x_h_x_d': 'Approx. 150.0 × 142.6 × 87.2mm'
            },
            'EOS R5': {
                'type_type_type': 'Digital interchangeable lens, mirrorless camera',
                'type_image_processor': 'DIGIC X',
                'type_recording_media': 'SD/SDHC/SDXC memory cards',
                'type_compatible_lenses': 'Canon RF lens group (excluding EF, EF-S and EF-M lenses)When using Mount Adapter EF-EOS R: Canon EF or EF-S lenses (excluding EF-M lenses)',
                'type_lens_mount': 'Canon RF mount',
                'type_image_sensor_type': 'CMOS sensor (compatible with Dual Pixel CMOS AF)',
                'type_viewfinder_type': 'OLED color electronic viewfinder',
                'type_shutter_type': 'Electronically controlled focal-plane shutter',
                'type_lcd_screen_type': 'TFT color, liquid-crystal monitor',
                'effective_pixels': 'Approx. 45.0 megapixels',
                'total_pixels': 'Approx. 46.1 megapixels',
                'screen_size': '3.2-inch (screen aspect ratio of 3:2)',
                'pixel_unit': 'Approx. 4.4 micro square',
                'weight': 'Approx. 738g (including battery and memory card)',
                'dimensions_w_x_h_x_d': 'Approx. 138.5 × 97.5 × 88.0mm'
            }
        }
        
        # Default values for missing attributes
        reference['defaults'] = {
            'audio_recording': 'Built-in microphone, External microphone input',
            'bluetooth_pairing': 'Bluetooth 4.2',
            'wifi': 'IEEE 802.11b/g/n (2.4GHz)',
            'usb_terminal': 'USB Type-C',
            'hdmi_out_terminal': 'HDMI Type D',
            'microphone_input_terminal': '3.5mm stereo mini-jack',
            'headphone_terminal': '3.5mm stereo mini-jack',
            'remote_control_terminal': 'N3-type terminal',
            'accessory_shoe': 'Multi-function shoe',
            'battery': 'LP-E6NH (included)',
            'battery_check': 'Automatic battery check',
            'startup_time': 'Approx. 0.4 seconds',
            'working_temperature_range': '0°C to 40°C (32°F to 104°F)',
            'working_humidity': '85% or less',
            'protection': 'File protection system',
            'erase': 'File deletion options',
            'dpof': 'Digital Print Order Format',
            'customization': 'Custom function options',
            'interface_languages': 'English, French, German, Italian, Spanish, Portuguese, Dutch, Russian, Japanese, Chinese (Simplified), Chinese (Traditional), Korean'
        }
        
        return reference
    
    def create_enrichment_template(self):
        """Create a structured template for manual enrichment."""
        
        if not self.input_file.exists():
            print("❌ Input file not found")
            return
        
        # Load current data
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create enrichment template
        template = {
            'metadata': {
                'total_cameras': len(data),
                'total_attributes': 223,
                'enrichment_guidelines': [
                    'Use exact values from Canon specifications when available',
                    'Maintain consistent formatting across all cameras',
                    'Use "N/A" for truly unavailable specifications',
                    'Use "Not specified" for unknown values',
                    'Preserve existing JSON structure'
                ]
            },
            'enrichment_data': {}
        }
        
        # Analyze empty attributes
        empty_attributes = defaultdict(list)
        
        for camera in data:
            camera_name = camera['product']
            template['enrichment_data'][camera_name] = {}
            
            for key, value in camera.items():
                if key != 'product' and isinstance(value, dict) and value.get('value') == '':
                    empty_attributes[key].append(camera_name)
                    template['enrichment_data'][camera_name][key] = {
                        'current_value': '',
                        'suggested_value': self.get_suggested_value(key, camera_name),
                        'source': self.get_value_source(key, camera_name),
                        'notes': ''
                    }
        
        # Save template
        template_file = Path("canon_enrichment_template.json")
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Enrichment template saved to: {template_file}")
        print(f"📊 Found {len(empty_attributes)} unique empty attributes")
        
        return template
    
    def get_suggested_value(self, attribute, camera_name):
        """Get suggested value for an attribute based on reference data."""
        
        # Check camera-specific values first
        if camera_name in self.reference_data['camera_specific']:
            if attribute in self.reference_data['camera_specific'][camera_name]:
                return self.reference_data['camera_specific'][camera_name][attribute]
        
        # Check common values
        if attribute in self.reference_data['common_values']:
            return self.reference_data['common_values'][attribute]
        
        # Check defaults
        if attribute in self.reference_data['defaults']:
            return self.reference_data['defaults'][attribute]
        
        return "N/A"
    
    def get_value_source(self, attribute, camera_name):
        """Get the source for a suggested value."""
        
        if camera_name in self.reference_data['camera_specific'] and attribute in self.reference_data['camera_specific'][camera_name]:
            return "camera_specific"
        elif attribute in self.reference_data['common_values']:
            return "common_values"
        elif attribute in self.reference_data['defaults']:
            return "defaults"
        else:
            return "manual_research"
    
    def apply_enrichment(self, enrichment_file):
        """Apply enrichment data to the comprehensive JSON file."""
        
        if not self.input_file.exists():
            print("❌ Input file not found")
            return
        
        if not Path(enrichment_file).exists():
            print("❌ Enrichment file not found")
            return
        
        # Create backup
        import shutil
        shutil.copy2(self.input_file, self.backup_file)
        print(f"📦 Backup created: {self.backup_file}")
        
        # Load data
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(enrichment_file, 'r', encoding='utf-8') as f:
            enrichment = json.load(f)
        
        # Apply enrichment
        updated_count = 0
        
        for camera in data:
            camera_name = camera['product']
            
            if camera_name in enrichment['enrichment_data']:
                for attr, enrichment_info in enrichment['enrichment_data'][camera_name].items():
                    if attr in camera and isinstance(camera[attr], dict):
                        new_value = enrichment_info.get('suggested_value', '')
                        if new_value and new_value != 'N/A':
                            camera[attr]['value'] = new_value
                            updated_count += 1
        
        # Save enriched data
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Enrichment applied! Updated {updated_count} attributes")
        print(f"📄 Enriched data saved to: {self.output_file}")
    
    def validate_enrichment(self):
        """Validate the enriched data structure."""
        
        if not self.output_file.exists():
            print("❌ Enriched file not found")
            return
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"🔍 Validating enriched data...")
        print(f"📊 Cameras: {len(data)}")
        
        # Check structure integrity
        structure_errors = 0
        empty_count = 0
        
        for camera in data:
            for key, value in camera.items():
                if key != 'product':
                    if not isinstance(value, dict):
                        structure_errors += 1
                    elif value.get('value') == '':
                        empty_count += 1
        
        print(f"✅ Structure errors: {structure_errors}")
        print(f"📭 Remaining empty attributes: {empty_count}")
        
        if structure_errors == 0:
            print("🎯 Enrichment validation: PASSED")
        else:
            print("⚠️  Enrichment validation: ISSUES DETECTED")

def main():
    """Main function for data enrichment."""
    enricher = CanonDataEnrichment()
    
    print("🎯 Canon Data Enrichment System")
    print("=" * 50)
    
    # Create enrichment template
    print("\n1. Creating enrichment template...")
    enricher.create_enrichment_template()
    
    print("\n2. Next steps:")
    print("   - Edit canon_enrichment_template.json with actual values")
    print("   - Run: enricher.apply_enrichment('canon_enrichment_template.json')")
    print("   - Run: enricher.validate_enrichment()")

if __name__ == "__main__":
    main()
