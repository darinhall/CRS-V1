#!/usr/bin/env python3
"""
Canon Mirrorless Camera Parser

This script processes Canon mirrorless camera HTML files and generates a normalized JSON structure
that matches the body_mirrorless.json schema format.
"""

import json
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import html


class CanonMirrorlessParser:
    """Parser for Canon mirrorless camera specifications."""
    
    def __init__(self):
        self.data_dir = Path("data/company_product/canon/raw_html")
        self.output_file = Path("data/company_product/canon/processed_data/schema/body_mirrorless2.json")
        self.mirrorless_cameras = []
        
        # Define the 13 mirrorless cameras to process
        self.target_cameras = [
            "eos-r1",
            "eos-r3", 
            "eos-r5",
            "eos-r5-mark-ii",
            "eos-r6-mark-ii",
            "eos-r7",
            "eos-r8",
            "eos-r10",
            "eos-r50",
            "eos-r100",
            "eos-r5-c",
            "eos-r50-v-body",
            "eos-rp"
        ]
        
        # Schema template based on body_mirrorless.json
        self.schema_template = {
            "product": "",
            "image_processor": {"metadata": {"table": False}, "value": ""},
            "recording_media": {"metadata": {"table": False}, "value": ""},
            "compatible_lens": {"metadata": {"table": False}, "value": ""},
            "lens_mount": {"metadata": {"table": False}, "value": ""},
            "effective_pixels": {"metadata": {"table": False}, "value": ""},
            "screen_size": {"metadata": {"table": False}, "value": ""},
            "lcd_monitor_size": {"metadata": {"table": False}, "value": ""},
            "pixel_unit": {"metadata": {"table": False}, "value": ""},
            "total_pixels": {"metadata": {"table": False}, "value": ""},
            "aspect_ratio": {"metadata": {"table": False}, "value": ""},
            "color_filter_system": {"metadata": {"table": False}, "value": ""},
            "low_pass_filter": {"metadata": {"table": False}, "value": ""},
            "dust_deletion_feature": {"metadata": {"table": False}, "value": ""},
            "recording_format": {"metadata": {"table": False}, "value": ""},
            "image_format": {"metadata": {"table": False}, "value": ""},
            "file_size": {"metadata": {"table": True}},
            "file_numbering": {"metadata": {"table": False}, "value": ""},
            "raw_+_jpeg_/_heif_simultaneous_recording": {"metadata": {"table": False}, "value": ""},
            "color_space": {"metadata": {"table": False}, "value": ""},
            "white_balance": {"metadata": {"table": False}, "value": ""},
            "auto_white_balance": {"metadata": {"table": False}, "value": ""},
            "white_balance_shift": {"metadata": {"table": False}, "value": ""},
            "coverage": {"metadata": {"table": False}, "value": ""},
            "magnification_/_angle_of_view": {"metadata": {"table": False}, "value": ""},
            "eye_point": {"metadata": {"table": False}, "value": ""},
            "dioptric_adjustment_range": {"metadata": {"table": False}, "value": ""},
            "viewfinder_information": {"metadata": {"table": False}, "value": ""},
            "focus_method": {"metadata": {"table": False}, "value": ""},
            "number_of_af_zones_available_for_automatic_selection": {"metadata": {"table": False}, "value": ""},
            "selectable_positions_for_af_point": {"metadata": {"table": False}, "value": ""},
            "af_work_range": {"metadata": {"table": False}, "value": ""},
            "focusing_brightness_range_still_photo": {"metadata": {"table": False}, "value": ""},
            "focusing_brightness_range_video": {"metadata": {"table": False}, "value": ""},
            "available_af_areas": {"metadata": {"table": False}, "value": ""},
            "available_subject_detection": {"metadata": {"table": False}, "value": ""}
        }
    
    def find_mirrorless_camera_files(self):
        """Find all mirrorless camera HTML files."""
        print("🔍 Finding mirrorless camera files...")
        
        for camera in self.target_cameras:
            file_path = self.data_dir / f"{camera}.html"
            if file_path.exists():
                self.mirrorless_cameras.append(file_path)
                print(f"  ✅ Found: {camera}.html")
            else:
                print(f"  ❌ Missing: {camera}.html")
        
        print(f"📊 Found {len(self.mirrorless_cameras)} out of {len(self.target_cameras)} target cameras")
        return self.mirrorless_cameras
    
    def normalize_html_tables(self, soup):
        """Normalize HTML tables by removing rowspan and colspan attributes."""
        print("  🔧 Normalizing HTML tables...")
        
        # Find all tables
        tables = soup.find_all('table')
        
        for table in tables:
            # Remove rowspan and colspan attributes
            for cell in table.find_all(['td', 'th']):
                if cell.has_attr('rowspan'):
                    del cell['rowspan']
                if cell.has_attr('colspan'):
                    del cell['colspan']
        
        return soup
    
    def extract_specifications(self, file_path):
        """Extract specifications from a camera HTML file."""
        camera_name = file_path.stem
        print(f"📷 Processing: {camera_name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Normalize tables
            soup = self.normalize_html_tables(soup)
            
            # Find the technical specifications section
            tech_spec_section = soup.find('div', id='tech-spec-data')
            if not tech_spec_section:
                print(f"  ⚠️  No technical specifications found in {camera_name}")
                return self.create_empty_spec(camera_name)
            
            # Extract camera specifications
            camera_data = self._extract_camera_specs(tech_spec_section, camera_name)
            
            # Debug output for all cameras
            print(f"  🔍 Debug: Found {len(camera_data['attribution_group_details'])} specification groups")
            for group_name, group_details in camera_data['attribution_group_details'].items():
                print(f"    📋 Group: {group_name}")
                print(f"      Attributes: {group_details['attributes']}")
                for attr_name in group_details['attributes']:
                    if 'type' in attr_name.lower():
                        print(f"      🔍 Type attribute '{attr_name}': {group_details['values'].get(attr_name, '')}")
            
            # Convert to schema format
            schema_data = self.convert_to_schema_format(camera_data, camera_name)
            
            print(f"  ✅ Extracted {len(camera_data['spec_attributes'])} specifications")
            return schema_data
            
        except Exception as e:
            print(f"  ❌ Error processing {camera_name}: {e}")
            return self.create_empty_spec(camera_name)
    
    def _extract_camera_specs(self, tech_spec_section, camera_name):
        """Extract specifications from a technical specifications section."""
        
        camera_data = {
            'camera_name': camera_name,
            'attribution_groups': [],
            'spec_attributes': [],
            'spec_values': {},
            'attribution_group_details': {},
            'table_data': {}
        }
        
        # Find all attribution groups (h3 tags within tech-spec sections)
        attribution_groups = tech_spec_section.find_all('h3')
        
        for group in attribution_groups:
            group_name = group.get_text(strip=True)
            
            # Skip non-specification groups
            if any(skip in group_name.lower() for skip in ['view full', 'pdf', 'expand']):
                continue
            
            camera_data['attribution_groups'].append(group_name)
            
            # Find the parent container for this attribution group
            group_container = group.find_parent('div', class_='tech-spec')
            if not group_container:
                continue
            
            # Find all spec attributes within this group
            spec_attrs = group_container.find_all('div', class_='tech-spec-attr')
            
            group_details = {
                'attributes': [],
                'values': {}
            }
            
            # Process spec attributes in pairs (attribute name and value)
            for i in range(0, len(spec_attrs), 2):
                if i + 1 < len(spec_attrs):
                    attr_div = spec_attrs[i]
                    value_div = spec_attrs[i + 1]
                    
                    # Extract attribute name
                    attr_name = attr_div.get_text(strip=True)
                    if not attr_name:
                        continue
                    
                    # Check if the value div contains a table
                    table = value_div.find('table')
                    if table:
                        # Extract table data
                        table_data = self._extract_table_data(table, attr_name)
                        camera_data['table_data'][attr_name] = table_data
                        continue
                    
                    # Extract attribute value
                    attr_value = value_div.get_text(strip=True)
                    
                    # Clean up the attribute name and value
                    attr_name = self._clean_text(attr_name)
                    attr_value = self._clean_text(attr_value)
                    
                    if attr_name and attr_value:
                        camera_data['spec_attributes'].append(attr_name)
                        camera_data['spec_values'][attr_name] = attr_value
                        group_details['attributes'].append(attr_name)
                        group_details['values'][attr_name] = attr_value
            
            camera_data['attribution_group_details'][group_name] = group_details
        
        return camera_data
    
    def _extract_table_data(self, table, group_name):
        """Extract data from HTML tables and normalize it."""
        table_data = {}
        
        # Check if this is a file size table
        if 'file size' in group_name.lower() or 'recording format' in group_name.lower():
            return self._parse_file_size_table(table)
        
        # Find all rows
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                # First cell is usually the key, second is the value
                key = self._clean_text(cells[0].get_text())
                value = self._clean_text(cells[1].get_text())
                
                if key and value:
                    table_data[key] = value
        
        return table_data
    
    def _parse_file_size_table(self, table):
        """Parse complex file size tables with nested data structures."""
        table_data = {}
        
        # Find all rows
        rows = table.find_all('tr')
        
        # Skip header row
        if len(rows) < 2:
            return table_data
        
        # Process data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:
                continue
            
            # Get the format type (first cell)
            format_type = self._clean_text(cells[0].get_text())
            if not format_type or format_type == '' or format_type == '&nbsp;':
                continue
            
            # Initialize format data
            if format_type not in table_data:
                table_data[format_type] = {}
            
            # Get the quality level (second cell)
            quality = self._clean_text(cells[1].get_text())
            if not quality or quality == '' or quality == '&nbsp;':
                continue
            
            # Create format data object
            format_data = {}
            
            # Extract file size (third cell)
            if len(cells) >= 3:
                file_size = self._clean_text(cells[2].get_text())
                if file_size and file_size != '' and file_size != '&nbsp;':
                    format_data['file_size_mb'] = file_size
            
            # Extract possible shots (fourth cell)
            if len(cells) >= 4:
                possible_shots = self._clean_text(cells[3].get_text())
                if possible_shots and possible_shots != '' and possible_shots != '&nbsp;':
                    format_data['possible_shots'] = possible_shots
            
            # Extract max burst (fifth cell)
            if len(cells) >= 5:
                max_burst = self._clean_text(cells[4].get_text())
                if max_burst and max_burst != '' and max_burst != '&nbsp;':
                    format_data['max_burst'] = max_burst
            
            # Only add if we have meaningful data
            if format_data:
                table_data[format_type][quality] = format_data
        
        return table_data
    
    def _clean_text(self, text):
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common HTML artifacts
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        return text
    
    def convert_to_schema_format(self, camera_data, camera_name):
        """Convert extracted data to the schema format."""
        import copy
        schema_data = copy.deepcopy(self.schema_template)
        
        # Set the product name
        schema_data['product'] = camera_name.replace('-', ' ').upper()
        
        # Create a mapping to store all extracted attributes with their group context
        all_attributes = {}
        
        # First pass: collect all attributes with their group context
        for group_name, group_details in camera_data['attribution_group_details'].items():
            for attr_name in group_details['attributes']:
                attr_value = group_details['values'].get(attr_name, '')
                
                # Create a unique key by combining group name and attribute name
                # Clean and normalize the group name for use as a prefix
                group_prefix = self._clean_text(group_name).lower().replace(' ', '_').replace('-', '_')
                attr_clean = self._clean_text(attr_name).lower().replace(' ', '_').replace('-', '_')
                
                # Create unique key: ONLY append group prefix if the attribute name is "type"
                # This prevents confusion between multiple "type" attributes in different groups
                if attr_clean.lower() == 'type':
                    unique_key = f"type_{group_prefix}"
                else:
                    unique_key = attr_clean
                
                # Store the attribute with its context
                all_attributes[unique_key] = {
                    'value': attr_value,
                    'original_name': attr_name,
                    'group': group_name,
                    'unique_key': unique_key
                }
        
        # Improved spec mapping with context awareness - REMOVED generic 'type' mapping
        spec_mapping = {
            'image_processor': {
                'patterns': ['image processor', 'processor', 'digic'],
                'context_groups': ['type']
            },
            'recording_media': {
                'patterns': ['recording media', 'media', 'storage'],
                'context_groups': ['type']
            },
            'compatible_lens': {
                'patterns': ['compatible lens', 'lens compatibility'],
                'context_groups': ['type']
            },
            'lens_mount': {
                'patterns': ['lens mount', 'mount', 'rf mount', 'ef mount'],
                'context_groups': ['type']
            },
            'effective_pixels': {
                'patterns': ['effective pixels', 'effective pixel', 'resolution'],
                'context_groups': ['image sensor']
            },
            'screen_size': {
                'patterns': ['screen size'],
                'context_groups': ['image sensor']
            },
            'lcd_monitor_size': {
                'patterns': ['monitor size'],
                'context_groups': ['lcd screen']
            },
            'pixel_unit': {
                'patterns': ['pixel unit', 'pixel size'],
                'context_groups': ['image sensor']
            },
            'total_pixels': {
                'patterns': ['total pixels', 'total pixel'],
                'context_groups': ['image sensor']
            },
            'aspect_ratio': {
                'patterns': ['aspect ratio'],
                'context_groups': ['image sensor']
            },
            'color_filter_system': {
                'patterns': ['color filter system', 'color filter'],
                'context_groups': ['image sensor']
            },
            'low_pass_filter': {
                'patterns': ['low pass filter', 'low-pass filter'],
                'context_groups': ['image sensor']
            },
            'dust_deletion_feature': {
                'patterns': ['dust deletion feature', 'dust deletion'],
                'context_groups': ['image sensor']
            },
            'recording_format': {
                'patterns': ['recording format', 'file format'],
                'context_groups': ['recording system']
            },
            'image_format': {
                'patterns': ['image format'],
                'context_groups': ['recording system']
            },
            'file_numbering': {
                'patterns': ['file numbering', 'numbering'],
                'context_groups': ['recording system']
            },
            'raw_+_jpeg_/_heif_simultaneous_recording': {
                'patterns': ['raw + jpeg', 'simultaneous recording'],
                'context_groups': ['recording system']
            },
            'color_space': {
                'patterns': ['color space'],
                'context_groups': ['recording system']
            },
            'white_balance': {
                'patterns': ['settings'],
                'context_groups': ['white balance']
            },
            'auto_white_balance': {
                'patterns': ['auto white balance', 'auto wb'],
                'context_groups': ['white balance']
            },
            'white_balance_shift': {
                'patterns': ['white balance shift', 'wb shift'],
                'context_groups': ['white balance']
            },
            'coverage': {
                'patterns': ['coverage'],
                'context_groups': ['viewfinder']
            },
            'magnification_/_angle_of_view': {
                'patterns': ['magnification', 'angle of view'],
                'context_groups': ['viewfinder']
            },
            'eye_point': {
                'patterns': ['eye point', 'eyepoint'],
                'context_groups': ['viewfinder']
            },
            'dioptric_adjustment_range': {
                'patterns': ['dioptric adjustment', 'dioptric'],
                'context_groups': ['viewfinder']
            },
            'viewfinder_information': {
                'patterns': ['viewfinder information', 'evf info'],
                'context_groups': ['viewfinder']
            },
            'focus_method': {
                'patterns': ['focus method', 'focusing'],
                'context_groups': ['autofocus']
            },
            'number_of_af_zones_available_for_automatic_selection': {
                'patterns': ['number of af zones', 'af zones', 'autofocus zones'],
                'context_groups': ['autofocus']
            },
            'selectable_positions_for_af_point': {
                'patterns': ['af point', 'autofocus point'],
                'context_groups': ['autofocus']
            },
            'af_work_range': {
                'patterns': ['af work range', 'autofocus range'],
                'context_groups': ['autofocus']
            },
            'focusing_brightness_range_still_photo': {
                'patterns': ['focusing brightness range', 'af brightness'],
                'context_groups': ['autofocus']
            },
            'focusing_brightness_range_video': {
                'patterns': ['focusing brightness range video', 'af brightness video'],
                'context_groups': ['autofocus']
            },
            'available_af_areas': {
                'patterns': ['available af areas', 'af areas'],
                'context_groups': ['autofocus']
            },
            'available_subject_detection': {
                'patterns': ['subject to detect', 'subject detection', 'available subjects'],
                'context_groups': ['autofocus']
            }
        }
        
        # Map specifications to schema fields with context awareness
        for schema_field, mapping_config in spec_mapping.items():
            patterns = mapping_config['patterns']
            context_groups = mapping_config.get('context_groups', [])
            exclude_patterns = mapping_config.get('exclude_patterns', [])
            
            # Find matching attributes within the correct context groups
            for group_name, group_details in camera_data['attribution_group_details'].items():
                # Check if this group is in the allowed context groups
                if context_groups and not any(context.lower() in group_name.lower() for context in context_groups):
                    continue
                

                
                # Look for matching attributes in this group
                for attr_name in group_details['attributes']:
                    attr_value = group_details['values'].get(attr_name, '')
                    
                    # Check if any pattern matches
                    pattern_matched = False
                    for pattern in patterns:
                        if pattern.lower() in attr_name.lower():
                            pattern_matched = True
                            break
                    
                    if not pattern_matched:
                        continue
                    
                    # Check exclusion patterns
                    should_exclude = False
                    for exclude_pattern in exclude_patterns:
                        if exclude_pattern.lower() in attr_name.lower() or exclude_pattern.lower() in attr_value.lower():
                            should_exclude = True
                            break
                    
                    if should_exclude:
                        continue
                    
                    # Found a match! Set the value
                    if schema_field == 'file_size' and schema_field in camera_data['table_data']:
                        # Handle table data for file_size
                        schema_data[schema_field] = camera_data['table_data'].get('file_size', {})
                    else:
                        # Handle regular value
                        schema_data[schema_field]['value'] = attr_value
                    
                    # Break out of attribute loop since we found a match
                    break
                
                # Break out of group loop if we found a match for this schema field
                if schema_field in schema_data and schema_data[schema_field].get('value'):
                    break
        
        # Handle special cases for table data
        for group_name, table_data in camera_data['table_data'].items():
            if 'file size' in group_name.lower() or 'recording format' in group_name.lower():
                schema_data['file_size'] = table_data
        
        # Create a new ordered schema with type attributes in the correct positions
        from collections import OrderedDict
        ordered_schema = OrderedDict()
        
        # Add product first
        ordered_schema['product'] = schema_data['product']
        
        # Add type attributes first (in order of appearance in HTML)
        type_attributes = OrderedDict()
        for unique_key, attr_info in all_attributes.items():
            if unique_key.startswith('type_'):
                type_attributes[unique_key] = {
                    'metadata': {'table': False},
                    'value': attr_info['value']
                }
        
        # Add type attributes in order
        for key, value in type_attributes.items():
            ordered_schema[key] = value
        
        # Add all other schema fields
        for key, value in schema_data.items():
            if key != 'product' and not key.startswith('type_'):
                ordered_schema[key] = value
        
        return ordered_schema
    
    def create_empty_spec(self, camera_name):
        """Create an empty specification entry for cameras with missing data."""
        schema_data = self.schema_template.copy()
        schema_data['product'] = camera_name.replace('-', ' ').upper()
        return schema_data
    
    def process_all_cameras(self):
        """Process all mirrorless cameras and generate the JSON file."""
        print("🚀 Starting Canon mirrorless camera processing...")
        
        # Find camera files
        camera_files = self.find_mirrorless_camera_files()
        
        if not camera_files:
            print("❌ No camera files found!")
            return
        
        # Process each camera
        all_camera_data = []
        
        for file_path in camera_files:
            camera_data = self.extract_specifications(file_path)
            all_camera_data.append(camera_data)
        
        # Save to JSON file
        self.save_to_json(all_camera_data)
        
        print(f"✅ Processing complete! Generated data for {len(all_camera_data)} cameras")
    
    def save_to_json(self, camera_data):
        """Save camera data to JSON file."""
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(camera_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Data saved to: {self.output_file}")


def main():
    """Main function to run the parser."""
    parser = CanonMirrorlessParser()
    parser.process_all_cameras()


if __name__ == "__main__":
    main()
