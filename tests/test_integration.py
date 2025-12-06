import unittest
import tempfile
import subprocess
import sys
from pathlib import Path


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete application."""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        
        # Create complete test directory structure
        prompts_dir = self.base_path / "prompts"
        (prompts_dir / "general").mkdir(parents=True)
        (prompts_dir / "grapes" / "articles").mkdir(parents=True)
        (prompts_dir / "regions").mkdir(parents=True)
        
        # Create all necessary prompt files
        (prompts_dir / "general" / "system_prompt.md").write_text("Integration test system prompt")
        (prompts_dir / "grapes" / "technical_prompt.md").write_text("Integration test technical prompt")
        (prompts_dir / "grapes" / "art_prompt.md").write_text("Integration test story prompt")
        (prompts_dir / "regions" / "region_research_prompt.md").write_text("Integration test region prompt")
        
        # Create test variety
        variety_context = """---
name: "Integration Test Grape"
prompt: "A grape variety for integration testing"
---"""
        (prompts_dir / "grapes" / "articles" / "integrationgrape.md").write_text(variety_context)
        
        # Create test region
        region_context = """---
name: "Integration Test Region"
summary: "A wine region for integration testing"
known_varieties: ["Test Grape"]
---"""
        (prompts_dir / "regions" / "integration_region.md").write_text(region_context)
        
        # Copy main.py to temp directory for testing
        main_py_source = Path.cwd() / "main.py"
        self.main_py_path = self.base_path / "main.py"
        
        if main_py_source.exists():
            main_content = main_py_source.read_text()
            # Update the import paths for the test environment
            main_content = main_content.replace(
                "from src.grapegeek.grape_article_generator import GrapeArticleGenerator",
                f"import sys; sys.path.append('{Path.cwd()}'); from src.grapegeek.grape_article_generator import GrapeArticleGenerator"
            )
            main_content = main_content.replace(
                "from src.grapegeek.region_researcher import RegionResearcher",
                f"from src.grapegeek.region_researcher import RegionResearcher"
            )
            self.main_py_path.write_text(main_content)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def run_main_script(self, args):
        """Helper method to run the main script with given arguments."""
        # Change to temp directory for the test
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(str(self.base_path))
            
            # Add current working directory to sys.path so imports work
            if str(original_cwd) not in sys.path:
                sys.path.insert(0, str(original_cwd))
            
            # Import and run main function
            sys.argv = ['main.py'] + args
            
            from main import main
            main()
            
        finally:
            os.chdir(str(original_cwd))
    
    def test_grape_technical_dry_run(self):
        """Test grape technical article generation with dry run."""
        try:
            self.run_main_script(['grape', 'integrationgrape', '--dry-run'])
            
            # Check that output file was created
            output_file = self.base_path / "output" / "articles" / "integrationgrape.md"
            self.assertTrue(output_file.exists())
            
            content = output_file.read_text()
            self.assertIn("[DRY RUN]", content)
            self.assertIn("Integration Test Grape", content)
            
        except SystemExit as e:
            # Expected exit code 0 for success
            self.assertEqual(e.code, None or 0)
    
    def test_grape_story_dry_run(self):
        """Test grape story article generation with dry run."""
        try:
            self.run_main_script(['grape', 'integrationgrape', '--type', 'story', '--dry-run'])
            
            # Check that output file was created
            output_file = self.base_path / "output" / "articles" / "integrationgrape_winemaking_stories.md"
            self.assertTrue(output_file.exists())
            
            content = output_file.read_text()
            self.assertIn("[DRY RUN]", content)
            self.assertIn("Integration test story prompt", content)
            
        except SystemExit as e:
            # Expected exit code 0 for success
            self.assertEqual(e.code, None or 0)
    
    def test_region_research_dry_run(self):
        """Test region research with dry run."""
        try:
            self.run_main_script(['region', 'integration region', '--dry-run'])
            
            # Check that output file was created
            output_file = self.base_path / "output" / "regions" / "integration_region_varieties.md"
            self.assertTrue(output_file.exists())
            
            content = output_file.read_text()
            self.assertIn("[DRY RUN]", content)
            self.assertIn("Integration Test Region", content)
            
        except SystemExit as e:
            # Expected exit code 0 for success
            self.assertEqual(e.code, None or 0)
    
    def test_help_command(self):
        """Test that help command works."""
        with self.assertRaises(SystemExit):
            self.run_main_script(['--help'])
    
    def test_no_command(self):
        """Test behavior when no command is provided."""
        with self.assertRaises(SystemExit) as cm:
            self.run_main_script([])
        
        self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    # Skip integration tests if we can't access the main module
    try:
        from pathlib import Path
        if not (Path.cwd() / "main.py").exists():
            print("Skipping integration tests - main.py not found")
            sys.exit(0)
        
        unittest.main()
    except ImportError as e:
        print(f"Skipping integration tests - import error: {e}")
        sys.exit(0)