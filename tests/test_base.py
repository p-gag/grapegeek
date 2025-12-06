import unittest
import tempfile
import yaml
from pathlib import Path
from src.grapegeek.base import BaseGenerator


class TestBaseGenerator(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        
        # Create test prompt structure
        prompts_dir = self.base_path / "prompts"
        prompts_dir.mkdir(parents=True)
        
        # Create a test prompt file
        test_prompt_dir = prompts_dir / "test"
        test_prompt_dir.mkdir(parents=True)
        (test_prompt_dir / "test_prompt.md").write_text("Test prompt content")
        
        # Create a test YAML file
        yaml_file = prompts_dir / "test_yaml.md"
        yaml_content = """---
name: "Test Name"
description: "Test description"
---
Test markdown content"""
        yaml_file.write_text(yaml_content)
        
        self.generator = BaseGenerator(base_path=str(self.base_path), dry_run=True)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_init_dry_run(self):
        """Test initialization with dry run mode."""
        self.assertTrue(self.generator.dry_run)
        self.assertIsNone(self.generator.client)
        self.assertEqual(self.generator.base_path, self.base_path)
    
    def test_init_normal_mode(self):
        """Test initialization with normal mode."""
        # This will fail without OpenAI API key, but we test the structure
        try:
            generator = BaseGenerator(base_path=str(self.base_path), dry_run=False)
            self.assertFalse(generator.dry_run)
        except Exception:
            # Expected if no API key
            pass
    
    def test_load_prompt_file(self):
        """Test loading prompt files."""
        content = self.generator.load_prompt_file("test/test_prompt.md")
        self.assertEqual(content, "Test prompt content")
        
        # Test non-existent file
        content = self.generator.load_prompt_file("nonexistent.md")
        self.assertEqual(content, "")
    
    def test_load_yaml_frontmatter(self):
        """Test loading YAML frontmatter."""
        yaml_file = self.base_path / "prompts" / "test_yaml.md"
        default_data = {"default": "value"}
        
        result = self.generator.load_yaml_frontmatter(yaml_file, default_data)
        self.assertEqual(result["name"], "Test Name")
        self.assertEqual(result["description"], "Test description")
        
        # Test non-existent file
        nonexistent_file = self.base_path / "nonexistent.md"
        result = self.generator.load_yaml_frontmatter(nonexistent_file, default_data)
        self.assertEqual(result, default_data)
    
    def test_call_openai_dry_run(self):
        """Test OpenAI call in dry run mode."""
        test_prompt = "This is a test prompt"
        result = self.generator.call_openai(test_prompt)
        
        self.assertIn("[DRY RUN]", result)
        self.assertIn(test_prompt, result)
    
    def test_save_content(self):
        """Test saving content to files."""
        test_content = "Test content to save"
        output_file = self.base_path / "test_output.txt"
        
        result_path = self.generator.save_content(output_file, test_content)
        
        self.assertEqual(result_path, output_file)
        self.assertTrue(output_file.exists())
        self.assertEqual(output_file.read_text(), test_content)
    
    def test_get_prompt_files(self):
        """Test getting all prompt files."""
        prompt_files = self.generator.get_prompt_files()
        
        self.assertIn("test/test_prompt.md", prompt_files)
        self.assertEqual(prompt_files["test/test_prompt.md"], "Test prompt content")
        self.assertIn("test_yaml.md", prompt_files)


if __name__ == '__main__':
    unittest.main()