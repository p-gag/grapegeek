#!/usr/bin/env python3
"""
Unit tests for grape variety mapping functionality
"""

import unittest
import tempfile
import yaml
from pathlib import Path
from create_final_geojson import load_grape_variety_mapping, normalize_grape_variety

class TestGrapeMapping(unittest.TestCase):
    
    def setUp(self):
        """Set up test data with actual YAML structure"""
        self.test_yaml_data = {
            'grape_variety_mapping': {
                'Fruit': {
                    'aliases': [
                        'apple',
                        'apple (fruit wine)',
                        'apple (cider)',
                        'apples',
                        'blueberry',
                        'blueberry (fruit wine)',
                        'strawberry',
                        'cherry',
                        'peach'
                    ]
                },
                'Unknown': {
                    'aliases': [
                        'blend',
                        'blend (not specified)',
                        'cold-hardy hybrid (unspecified)',
                        'hybrid grapes (various)',
                        'red blend',
                        'white blend',
                        'unknown'
                    ]
                },
                'Acadie Blanc': {
                    'aliases': [
                        'acadie',
                        'acadie blanc',
                        "l'acadie blanc"
                    ]
                },
                'Frontenac Noir': {
                    'aliases': [
                        'frontenac',
                        'frontenac noir',
                        'frontenac (noir)',
                        'frontenac red'
                    ]
                },
                'Chardonnay': {
                    'aliases': [
                        'chardonnay',
                        'vitis vinifera - chardonnay'
                    ]
                },
                'Maréchal Foch': {
                    'aliases': [
                        'foch',
                        'maréchal foch',
                        'marechal foch'
                    ]
                }
            }
        }
        
        # Create a temporary file with test data
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(self.test_yaml_data, self.temp_file, default_flow_style=False, allow_unicode=True)
        self.temp_file.close()
        self.temp_file_path = Path(self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary file"""
        if self.temp_file_path.exists():
            self.temp_file_path.unlink()
    
    def test_load_grape_variety_mapping(self):
        """Test loading and building alias lookup map"""
        # Mock the mapping file path
        import create_final_geojson
        original_path = create_final_geojson.Path("data/grape_variety_mapping.yaml")
        create_final_geojson.Path = lambda x: self.temp_file_path if "grape_variety_mapping" in str(x) else original_path
        
        # Capture print output
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            alias_lookup = load_grape_variety_mapping()
            
            # Restore stdout
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            # Test that alias lookup map was built correctly
            self.assertIsInstance(alias_lookup, dict)
            
            # Test specific mappings
            self.assertEqual(alias_lookup['acadie'], 'Acadie Blanc')
            self.assertEqual(alias_lookup['acadie blanc'], 'Acadie Blanc')
            self.assertEqual(alias_lookup["l'acadie blanc"], 'Acadie Blanc')
            
            self.assertEqual(alias_lookup['frontenac'], 'Frontenac Noir')
            self.assertEqual(alias_lookup['frontenac noir'], 'Frontenac Noir')
            self.assertEqual(alias_lookup['frontenac red'], 'Frontenac Noir')
            
            self.assertEqual(alias_lookup['chardonnay'], 'Chardonnay')
            self.assertEqual(alias_lookup['vitis vinifera - chardonnay'], 'Chardonnay')
            
            self.assertEqual(alias_lookup['foch'], 'Maréchal Foch')
            self.assertEqual(alias_lookup['maréchal foch'], 'Maréchal Foch')
            
            # Test fruit mappings
            self.assertEqual(alias_lookup['apple'], 'Fruit')
            self.assertEqual(alias_lookup['blueberry'], 'Fruit')
            self.assertEqual(alias_lookup['strawberry'], 'Fruit')
            
            # Test unknown mappings
            self.assertEqual(alias_lookup['blend'], 'Unknown')
            self.assertEqual(alias_lookup['red blend'], 'Unknown')
            self.assertEqual(alias_lookup['unknown'], 'Unknown')
            
            # Test stats in output
            self.assertIn('Grape variety mapping loaded:', output)
            self.assertIn('Total entries: 6', output)
            self.assertIn('Alias lookup map:', output)
            
        finally:
            # Restore original Path
            import create_final_geojson
            create_final_geojson.Path = Path
    
    def test_normalize_grape_variety(self):
        """Test grape variety normalization"""
        # Build alias lookup map manually for testing
        alias_lookup = {
            'acadie': 'Acadie Blanc',
            'acadie blanc': 'Acadie Blanc',
            "l'acadie blanc": 'Acadie Blanc',
            'frontenac': 'Frontenac Noir',
            'frontenac noir': 'Frontenac Noir',
            'frontenac red': 'Frontenac Noir',
            'chardonnay': 'Chardonnay',
            'foch': 'Maréchal Foch',
            'maréchal foch': 'Maréchal Foch',
            'apple': 'Fruit',
            'blueberry': 'Fruit',
            'blend': 'Unknown',
            'red blend': 'Unknown'
        }
        
        # Test exact matches
        self.assertEqual(normalize_grape_variety('acadie', alias_lookup), 'Acadie Blanc')
        self.assertEqual(normalize_grape_variety('Acadie Blanc', alias_lookup), 'Acadie Blanc')
        self.assertEqual(normalize_grape_variety('FRONTENAC', alias_lookup), 'Frontenac Noir')
        self.assertEqual(normalize_grape_variety('  frontenac noir  ', alias_lookup), 'Frontenac Noir')
        
        # Test case insensitivity and whitespace handling
        self.assertEqual(normalize_grape_variety('CHARDONNAY', alias_lookup), 'Chardonnay')
        self.assertEqual(normalize_grape_variety('  Maréchal Foch  ', alias_lookup), 'Maréchal Foch')
        
        # Test fruits
        self.assertEqual(normalize_grape_variety('apple', alias_lookup), 'Fruit')
        self.assertEqual(normalize_grape_variety('BLUEBERRY', alias_lookup), 'Fruit')
        
        # Test unknown/blends
        self.assertEqual(normalize_grape_variety('blend', alias_lookup), 'Unknown')
        self.assertEqual(normalize_grape_variety('Red Blend', alias_lookup), 'Unknown')
        
        # Test unmapped varieties (should return original)
        self.assertEqual(normalize_grape_variety('Some Unknown Variety', alias_lookup), 'Some Unknown Variety')
        self.assertEqual(normalize_grape_variety('Fake Grape', alias_lookup), 'Fake Grape')
        
        # Test edge cases
        self.assertEqual(normalize_grape_variety('', alias_lookup), '')
        self.assertEqual(normalize_grape_variety(None, alias_lookup), None)
        self.assertEqual(normalize_grape_variety('test', {}), 'test')  # Empty mapping
    
    def test_alias_case_sensitivity(self):
        """Test that alias matching is case insensitive"""
        alias_lookup = {
            'frontenac noir': 'Frontenac Noir',
            'maréchal foch': 'Maréchal Foch'
        }
        
        # Test various case combinations
        test_cases = [
            ('Frontenac Noir', 'Frontenac Noir'),
            ('FRONTENAC NOIR', 'Frontenac Noir'),
            ('frontenac noir', 'Frontenac Noir'),
            ('FrOnTeNaC nOiR', 'Frontenac Noir'),
            ('Maréchal Foch', 'Maréchal Foch'),
            ('MARÉCHAL FOCH', 'Maréchal Foch'),
            ('maréchal foch', 'Maréchal Foch')
        ]
        
        for input_variety, expected in test_cases:
            result = normalize_grape_variety(input_variety, alias_lookup)
            self.assertEqual(result, expected, f"Failed for input: '{input_variety}'")
    
    def test_whitespace_handling(self):
        """Test that whitespace is properly handled"""
        alias_lookup = {
            'frontenac noir': 'Frontenac Noir',
            'acadie blanc': 'Acadie Blanc'
        }
        
        test_cases = [
            ('  frontenac noir  ', 'Frontenac Noir'),
            ('\tfrontenac noir\n', 'Frontenac Noir'),
            ('   ACADIE BLANC   ', 'Acadie Blanc'),
            (' \t acadie blanc \n ', 'Acadie Blanc')
        ]
        
        for input_variety, expected in test_cases:
            result = normalize_grape_variety(input_variety, alias_lookup)
            self.assertEqual(result, expected, f"Failed for input: '{repr(input_variety)}'")

if __name__ == '__main__':
    # Run the tests with verbose output
    unittest.main(verbosity=2)