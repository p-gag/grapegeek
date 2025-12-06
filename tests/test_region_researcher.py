import unittest
import tempfile
from pathlib import Path
from src.grapegeek.region_researcher import RegionResearcher


class TestRegionResearcher(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        
        # Create test directory structure
        prompts_dir = self.base_path / "prompts"
        (prompts_dir / "general").mkdir(parents=True)
        (prompts_dir / "regions").mkdir(parents=True)
        
        # Create test prompt files
        (prompts_dir / "general" / "system_prompt.md").write_text("System prompt for region research")
        (prompts_dir / "regions" / "region_research_prompt.md").write_text("Region research prompt template")
        
        # Create test region context
        region_context = """---
name: "Test Region"
summary: "A cold-climate test wine region"
known_varieties: ["Riesling", "Pinot Noir"]
trade_association: "Test Wine Association"
trade_association_url: "https://testwine.org"
---"""
        (prompts_dir / "regions" / "test_region.md").write_text(region_context)
        
        self.researcher = RegionResearcher(base_path=str(self.base_path), dry_run=True)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_init(self):
        """Test region researcher initialization."""
        self.assertTrue(self.researcher.dry_run)
        self.assertTrue((self.researcher.output_path / "regions").exists())
    
    def test_load_region_context(self):
        """Test loading region context."""
        context = self.researcher.load_region_context("test region")
        
        self.assertEqual(context["name"], "Test Region")
        self.assertEqual(context["summary"], "A cold-climate test wine region")
        self.assertEqual(context["known_varieties"], ["Riesling", "Pinot Noir"])
        self.assertEqual(context["trade_association"], "Test Wine Association")
        self.assertEqual(context["trade_association_url"], "https://testwine.org")
        
        # Test non-existent region
        context = self.researcher.load_region_context("nonexistent")
        self.assertEqual(context["name"], "nonexistent")
        self.assertNotIn("summary", context)
    
    def test_research_region_varieties_dry_run(self):
        """Test region research in dry run mode."""
        result = self.researcher.research_region_varieties("test region")
        
        self.assertIn("[DRY RUN]", result)
        self.assertIn("System prompt for region research", result)
        self.assertIn("Region research prompt template", result)
        self.assertIn("Test Region", result)
        self.assertIn("A cold-climate test wine region", result)
        self.assertIn("Riesling", result)
        self.assertIn("Test Wine Association", result)
        self.assertIn("https://testwine.org", result)
    
    def test_save_region_research(self):
        """Test saving region research."""
        test_content = "Test region research content"
        
        output_path = self.researcher.save_region_research("test region", test_content)
        expected_path = self.researcher.output_path / "regions" / "test_region_varieties.md"
        
        self.assertEqual(output_path, expected_path)
        self.assertTrue(expected_path.exists())
        self.assertEqual(expected_path.read_text(), test_content)
    
    def test_research_and_save(self):
        """Test complete region research and save process."""
        output_path = self.researcher.research_and_save("test region")
        
        self.assertTrue(output_path.exists())
        content = output_path.read_text()
        self.assertIn("[DRY RUN]", content)
        self.assertIn("Region research prompt template", content)
        self.assertTrue(output_path.name.endswith("_varieties.md"))
    
    def test_region_name_normalization(self):
        """Test that region names with spaces are properly normalized."""
        output_path = self.researcher.save_region_research("New York Finger Lakes", "test content")
        expected_name = "new_york_finger_lakes_varieties.md"
        
        self.assertEqual(output_path.name, expected_name)


if __name__ == '__main__':
    unittest.main()