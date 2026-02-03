"""Tests for language and framework detectors"""
import pytest
from pathlib import Path
from app.detectors.language import LanguageDetector
from app.detectors.framework import FrameworkDetector


class TestLanguageDetector:
    """Test language detection"""
    
    @pytest.fixture
    def test_project(self, tmp_path):
        """Create test project with multiple languages"""
        # Python files
        (tmp_path / "app.py").write_text("print('hello')")
        (tmp_path / "utils.py").write_text("def foo(): pass")
        (tmp_path / "test.py").write_text("import pytest")
        
        # JavaScript files
        (tmp_path / "index.js").write_text("console.log('hello')")
        (tmp_path / "app.js").write_text("const x = 1")
        
        return tmp_path
    
    def test_detect_multiple_languages(self, test_project):
        """Test detecting multiple languages"""
        detector = LanguageDetector()
        languages = detector.detect(test_project, min_files=1)
        
        assert "Python" in languages
        assert "JavaScript" in languages
        # Python should be first (more files)
        assert languages[0] == "Python"
    
    def test_ignore_node_modules(self, tmp_path):
        """Test that node_modules is ignored"""
        # Create node_modules with JS files
        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "lib.js").write_text("module.exports = {}")
        
        detector = LanguageDetector()
        languages = detector.detect(tmp_path)
        
        # Should not detect JavaScript from node_modules
        assert languages == []


class TestFrameworkDetector:
    """Test framework detection"""
    
    def test_detect_django(self, tmp_path):
        """Test Django detection"""
        (tmp_path / "manage.py").write_text("import django")
        
        detector = FrameworkDetector()
        framework = detector.detect(tmp_path)
        
        assert framework == "Django"
    
    def test_detect_nextjs(self, tmp_path):
        """Test Next.js detection"""
        (tmp_path / "package.json").write_text('{"dependencies": {"next": "13.0.0"}}')
        
        detector = FrameworkDetector()
        framework = detector.detect(tmp_path)
        
        assert framework == "Next.js"
    
    def test_detect_laravel(self, tmp_path):
        """Test Laravel detection"""
        (tmp_path / "artisan").write_text("#!/usr/bin/env php")
        
        detector = FrameworkDetector()
        framework = detector.detect(tmp_path)
        
        assert framework == "Laravel"
    
    def test_no_framework(self, tmp_path):
        """Test when no framework is detected"""
        detector = FrameworkDetector()
        framework = detector.detect(tmp_path)
        
        assert framework is None
