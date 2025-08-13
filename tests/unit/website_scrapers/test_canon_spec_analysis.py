import unittest
import json
import os
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
import re


class CanonSpecAnalysisTest(unittest.TestCase):
    """Test class to analyze differences in attribution groups and spec attributes between Canon mirrorless cameras."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_dir = Path("data/company_product/canon/raw_html")
        self.output_file = Path("tests/unit/website_scrapers/canon_mirrorless_spec_analysis.json")
        self.eos_r_files = []
        
        # Find all EOS R camera HTML files
        for file_path in self.data_dir.glob("eos-r*.html"):
            if file_path.is_file():
                self.eos_r_files.append(file_path)
        
        print(f"Found {len(self.eos_r_files)} EOS R camera files for analysis")
    
    def test_analyze_canon_mirrorless_specs(self):
        """Test to analyze and compare technical specifications across Canon mirrorless cameras."""
        
        # Initialize data structures
        all_attribution_groups = set()
        all_spec_attributes = set()
        camera_specs = {}
        attribution_group_frequency = Counter()
        spec_attribute_frequency = Counter()
        
        # Process each EOS R camera file
        for file_path in self.eos_r_files:
            camera_name = file_path.stem
            print(f"Processing: {camera_name}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find the technical specifications section
                tech_spec_section = soup.find('div', id='tech-spec-data')
                if not tech_spec_section:
                    print(f"  ⚠️  No technical specifications found in {camera_name}")
                    continue
                
                # Extract camera specifications
                camera_data = self._extract_camera_specs(tech_spec_section, camera_name)
                camera_specs[camera_name] = camera_data
                
                # Collect attribution groups and spec attributes
                for group_name in camera_data['attribution_groups']:
                    all_attribution_groups.add(group_name)
                    attribution_group_frequency[group_name] += 1
                
                for attr_name in camera_data['spec_attributes']:
                    all_spec_attributes.add(attr_name)
                    spec_attribute_frequency[attr_name] += 1
                
                print(f"  ✅ Found {len(camera_data['attribution_groups'])} attribution groups and {len(camera_data['spec_attributes'])} spec attributes")
                
            except Exception as e:
                print(f"  ❌ Error processing {camera_name}: {e}")
                continue
        
        # Analyze differences and similarities
        analysis_results = self._analyze_spec_differences(
            camera_specs, 
            all_attribution_groups, 
            all_spec_attributes,
            attribution_group_frequency,
            spec_attribute_frequency
        )
        
        # Save results to JSON file
        self._save_analysis_results(analysis_results)
        
        # Assertions to verify the analysis
        self.assertGreater(len(camera_specs), 0, "Should have processed at least one camera file")
        self.assertGreater(len(all_attribution_groups), 0, "Should have found attribution groups")
        self.assertGreater(len(all_spec_attributes), 0, "Should have found spec attributes")
        
        print(f"\n✅ Analysis complete! Results saved to: {self.output_file}")
        print(f"📊 Summary:")
        print(f"   - Processed {len(camera_specs)} cameras")
        print(f"   - Found {len(all_attribution_groups)} unique attribution groups")
        print(f"   - Found {len(all_spec_attributes)} unique spec attributes")
    
    def _extract_camera_specs(self, tech_spec_section, camera_name):
        """Extract specifications from a technical specifications section."""
        
        camera_data = {
            'camera_name': camera_name,
            'attribution_groups': [],
            'spec_attributes': [],
            'spec_values': {},
            'attribution_group_details': {}
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
    
    def _clean_text(self, text):
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common HTML artifacts
        text = re.sub(r'<[^>]+>', '', text)
        
        return text
    
    def _analyze_spec_differences(self, camera_specs, all_attribution_groups, all_spec_attributes, 
                                 attribution_group_frequency, spec_attribute_frequency):
        """Analyze differences and similarities between camera specifications."""
        
        analysis = {
            'summary': {
                'total_cameras_analyzed': len(camera_specs),
                'total_attribution_groups': len(all_attribution_groups),
                'total_spec_attributes': len(all_spec_attributes),
                'analysis_timestamp': str(Path().cwd())
            },
            'attribution_groups': {
                'all_groups': sorted(list(all_attribution_groups)),
                'frequency_analysis': dict(attribution_group_frequency.most_common()),
                'common_groups': [group for group, freq in attribution_group_frequency.most_common() if freq > 1],
                'unique_groups': [group for group, freq in attribution_group_frequency.items() if freq == 1]
            },
            'spec_attributes': {
                'all_attributes': sorted(list(all_spec_attributes)),
                'frequency_analysis': dict(spec_attribute_frequency.most_common()),
                'common_attributes': [attr for attr, freq in spec_attribute_frequency.most_common() if freq > 1],
                'unique_attributes': [attr for attr, freq in spec_attribute_frequency.items() if freq == 1]
            },
            'camera_comparisons': {},
            'value_variations': {},
            'recommendations': {}
        }
        
        # Analyze each camera's specifications
        for camera_name, camera_data in camera_specs.items():
            analysis['camera_comparisons'][camera_name] = {
                'attribution_groups_count': len(camera_data['attribution_groups']),
                'spec_attributes_count': len(camera_data['spec_attributes']),
                'attribution_groups': camera_data['attribution_groups'],
                'spec_attributes': camera_data['spec_attributes'],
                'missing_common_groups': [group for group in analysis['attribution_groups']['common_groups'] 
                                        if group not in camera_data['attribution_groups']],
                'missing_common_attributes': [attr for attr in analysis['spec_attributes']['common_attributes'] 
                                            if attr not in camera_data['spec_attributes']]
            }
        
        # Analyze value variations for common attributes
        for attr_name in analysis['spec_attributes']['common_attributes']:
            values = []
            cameras_with_attr = []
            
            for camera_name, camera_data in camera_specs.items():
                if attr_name in camera_data['spec_values']:
                    values.append(camera_data['spec_values'][attr_name])
                    cameras_with_attr.append(camera_name)
            
            if len(set(values)) > 1:  # Only include if there are different values
                analysis['value_variations'][attr_name] = {
                    'unique_values': list(set(values)),
                    'value_frequency': dict(Counter(values)),
                    'cameras_with_attribute': cameras_with_attr
                }
        
        # Generate recommendations for parser development
        analysis['recommendations'] = self._generate_parser_recommendations(analysis)
        
        return analysis
    
    def _generate_parser_recommendations(self, analysis):
        """Generate recommendations for parser development based on analysis."""
        
        recommendations = {
            'core_attribution_groups': [],
            'core_spec_attributes': [],
            'optional_attribution_groups': [],
            'optional_spec_attributes': [],
            'parser_structure_suggestions': [],
            'data_consistency_notes': []
        }
        
        # Identify core attribution groups (present in >50% of cameras)
        total_cameras = analysis['summary']['total_cameras_analyzed']
        threshold = max(2, total_cameras // 2)  # At least 2 cameras or 50%
        
        for group, freq in analysis['attribution_groups']['frequency_analysis'].items():
            if freq >= threshold:
                recommendations['core_attribution_groups'].append({
                    'name': group,
                    'frequency': freq,
                    'percentage': round((freq / total_cameras) * 100, 1)
                })
            else:
                recommendations['optional_attribution_groups'].append({
                    'name': group,
                    'frequency': freq,
                    'percentage': round((freq / total_cameras) * 100, 1)
                })
        
        # Identify core spec attributes (present in >50% of cameras)
        for attr, freq in analysis['spec_attributes']['frequency_analysis'].items():
            if freq >= threshold:
                recommendations['core_spec_attributes'].append({
                    'name': attr,
                    'frequency': freq,
                    'percentage': round((freq / total_cameras) * 100, 1)
                })
            else:
                recommendations['optional_spec_attributes'].append({
                    'name': attr,
                    'frequency': freq,
                    'percentage': round((freq / total_cameras) * 100, 1)
                })
        
        # Parser structure suggestions
        recommendations['parser_structure_suggestions'] = [
            "Use h3 tags to identify attribution groups",
            "Use div.tech-spec-attr pairs for attribute name and value extraction",
            "Handle missing attributes gracefully (not all cameras have all specs)",
            "Consider value normalization for consistent data storage",
            "Implement fallback parsing for variations in HTML structure"
        ]
        
        # Data consistency notes
        recommendations['data_consistency_notes'] = [
            f"Found {len(analysis['value_variations'])} attributes with varying values across cameras",
            f"Most common attribution group: {max(analysis['attribution_groups']['frequency_analysis'].items(), key=lambda x: x[1])[0] if analysis['attribution_groups']['frequency_analysis'] else 'None'}",
            f"Most common spec attribute: {max(analysis['spec_attributes']['frequency_analysis'].items(), key=lambda x: x[1])[0] if analysis['spec_attributes']['frequency_analysis'] else 'None'}"
        ]
        
        return recommendations
    
    def _save_analysis_results(self, analysis_results):
        """Save analysis results to JSON file."""
        
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Analysis results saved to: {self.output_file}")


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(CanonSpecAnalysisTest)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
