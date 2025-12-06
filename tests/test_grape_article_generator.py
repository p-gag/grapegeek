import unittest
import tempfile
from pathlib import Path
from src.grapegeek.grape_article_generator import GrapeArticleGenerator


class TestGrapeArticleGenerator(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        
        # Create test directory structure
        prompts_dir = self.base_path / "prompts"
        (prompts_dir / "general").mkdir(parents=True)
        (prompts_dir / "grapes" / "articles").mkdir(parents=True)
        
        # Create test prompt files
        (prompts_dir / "general" / "system_prompt.md").write_text("System prompt for grape articles")
        (prompts_dir / "grapes" / "technical_prompt.md").write_text("Technical article prompt template")
        (prompts_dir / "grapes" / "art_prompt.md").write_text("Winemaking story prompt template")
        
        # Create test variety context
        variety_context = """---
name: "Test Grape"
prompt: "A cold-climate test grape variety"
---"""
        (prompts_dir / "grapes" / "articles" / "testgrape.md").write_text(variety_context)
        
        self.generator = GrapeArticleGenerator(base_path=str(self.base_path), dry_run=True)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_init(self):
        """Test grape article generator initialization."""
        self.assertTrue(self.generator.dry_run)
        self.assertTrue((self.generator.output_path / "articles").exists())
    
    def test_load_variety_context(self):
        """Test loading variety context."""
        context = self.generator.load_variety_context("testgrape")
        
        self.assertEqual(context["name"], "Test Grape")
        self.assertEqual(context["prompt"], "A cold-climate test grape variety")
        
        # Test non-existent variety
        context = self.generator.load_variety_context("nonexistent")
        self.assertEqual(context["name"], "nonexistent")
        self.assertEqual(context["prompt"], "")
    
    def test_generate_technical_article_dry_run(self):
        """Test technical article generation in dry run mode."""
        result = self.generator.generate_technical_article("testgrape")
        
        self.assertIn("[DRY RUN]", result)
        self.assertIn("System prompt for grape articles", result)
        self.assertIn("Technical article prompt template", result)
        self.assertIn("Test Grape", result)
        self.assertIn("A cold-climate test grape variety", result)
    
    def test_generate_story_article_dry_run(self):
        """Test story article generation in dry run mode."""
        result = self.generator.generate_story_article("testgrape")
        
        self.assertIn("[DRY RUN]", result)
        self.assertIn("System prompt for grape articles", result)
        self.assertIn("Winemaking story prompt template", result)
        self.assertIn("Test Grape", result)
        self.assertIn("A cold-climate test grape variety", result)
    
    def test_save_article(self):
        """Test saving articles."""
        test_content = "Test article content"
        
        # Test technical article
        tech_output = self.generator.save_article("testgrape", test_content, "technical")
        expected_path = self.generator.output_path / "articles" / "testgrape.md"
        self.assertEqual(tech_output, expected_path)
        self.assertTrue(expected_path.exists())
        self.assertEqual(expected_path.read_text(), test_content)
        
        # Test story article
        story_output = self.generator.save_article("testgrape", test_content, "story")
        expected_path = self.generator.output_path / "articles" / "testgrape_winemaking_stories.md"
        self.assertEqual(story_output, expected_path)
        self.assertTrue(expected_path.exists())
        self.assertEqual(expected_path.read_text(), test_content)
    
    def test_generate_and_save_technical(self):
        """Test complete technical article generation and save process."""
        output_path = self.generator.generate_and_save("testgrape", "technical")
        
        self.assertTrue(output_path.exists())
        content = output_path.read_text()
        self.assertIn("[DRY RUN]", content)
        self.assertIn("Technical article prompt template", content)
    
    def test_generate_and_save_story(self):
        """Test complete story article generation and save process."""
        output_path = self.generator.generate_and_save("testgrape", "story")
        
        self.assertTrue(output_path.exists())
        content = output_path.read_text()
        self.assertIn("[DRY RUN]", content)
        self.assertIn("Winemaking story prompt template", content)
        self.assertTrue(output_path.name.endswith("_winemaking_stories.md"))


if __name__ == '__main__':
    unittest.main()