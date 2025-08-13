#!/usr/bin/env python3
"""
Script to extract unique spec attributes and map them to specific cameras.
"""

import json
from pathlib import Path
from collections import defaultdict

def extract_unique_attributes_mapping():
    """Extract unique attributes and map them to specific cameras."""
    
    # Load the analysis results
    json_file = Path("tests/unit/website_scrapers/canon_mirrorless_spec_analysis.json")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get unique attributes
    unique_attributes = data['spec_attributes']['unique_attributes']
    
    # Get camera comparisons to see which cameras have which attributes
    camera_comparisons = data['camera_comparisons']
    
    # Create mapping of unique attributes to cameras
    unique_attribute_mapping = defaultdict(list)
    
    print("🔍 ANALYZING UNIQUE SPEC ATTRIBUTES")
    print("=" * 60)
    print(f"Found {len(unique_attributes)} unique spec attributes\n")
    
    # For each unique attribute, find which cameras have it
    for attr in unique_attributes:
        cameras_with_attr = []
        
        for camera_name, camera_data in camera_comparisons.items():
            if attr in camera_data['spec_attributes']:
                cameras_with_attr.append(camera_name)
        
        unique_attribute_mapping[attr] = cameras_with_attr
    
    # Display results
    print("📋 UNIQUE SPEC ATTRIBUTES AND THEIR CAMERAS:")
    print("=" * 60)
    
    for i, (attr, cameras) in enumerate(unique_attribute_mapping.items(), 1):
        print(f"\n{i:2d}. {attr}")
        print(f"    📷 Found in {len(cameras)} camera(s):")
        
        for camera in cameras:
            # Clean up camera name for display
            clean_name = camera.replace('eos-', 'EOS ').replace('-', ' ').title()
            print(f"       • {clean_name}")
    
    # Summary statistics
    print(f"\n📊 SUMMARY:")
    print("=" * 60)
    
    # Count how many unique attributes each camera has
    camera_unique_count = defaultdict(int)
    for attr, cameras in unique_attribute_mapping.items():
        for camera in cameras:
            camera_unique_count[camera] += 1
    
    print(f"Cameras with the most unique attributes:")
    sorted_cameras = sorted(camera_unique_count.items(), key=lambda x: x[1], reverse=True)
    
    for camera, count in sorted_cameras[:10]:  # Top 10
        clean_name = camera.replace('eos-', 'EOS ').replace('-', ' ').title()
        print(f"  • {clean_name}: {count} unique attributes")
    
    # Attributes that appear in only one camera
    single_camera_attrs = [attr for attr, cameras in unique_attribute_mapping.items() if len(cameras) == 1]
    print(f"\nAttributes found in only ONE camera: {len(single_camera_attrs)}")
    
    for attr in single_camera_attrs:
        camera = unique_attribute_mapping[attr][0]
        clean_name = camera.replace('eos-', 'EOS ').replace('-', ' ').title()
        print(f"  • {attr} → {clean_name}")
    
    return unique_attribute_mapping

def analyze_value_variations():
    """Analyze the value variations section to show different spec values."""
    
    json_file = Path("tests/unit/website_scrapers/canon_mirrorless_spec_analysis.json")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    value_variations = data['value_variations']
    
    print(f"\n🔄 VALUE VARIATIONS ANALYSIS")
    print("=" * 60)
    print(f"Found {len(value_variations)} attributes with varying values across cameras\n")
    
    # Show some interesting examples
    interesting_attrs = [
        'Type', 'Recording Media', 'ISO Speed Range', 'Shutter Speeds', 
        'Dimensions (W x H x D)', 'Weight', 'Battery'
    ]
    
    for attr in interesting_attrs:
        if attr in value_variations:
            variation = value_variations[attr]
            print(f"📋 {attr}:")
            print(f"   Unique values: {len(variation['unique_values'])}")
            
            for value, count in variation['value_frequency'].items():
                percentage = (count / len(variation['cameras_with_attribute'])) * 100
                print(f"   • {value} ({count} cameras, {percentage:.1f}%)")
            print()

if __name__ == "__main__":
    print("Canon Mirrorless Camera - Unique Attributes Analysis")
    print("=" * 60)
    
    # Extract unique attributes mapping
    unique_mapping = extract_unique_attributes_mapping()
    
    # Analyze value variations
    analyze_value_variations()
    
    print("✅ Analysis complete!")
