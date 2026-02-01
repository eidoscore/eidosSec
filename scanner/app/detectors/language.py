"""Programming language detection"""
from pathlib import Path
from typing import List, Dict
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detect programming languages in a project by file extensions"""
    
    # File extension to language mapping
    EXTENSIONS: Dict[str, str] = {
        ".py": "Python",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".php": "PHP",
        ".rb": "Ruby",
        ".go": "Go",
        ".java": "Java",
        ".kt": "Kotlin",
        ".cs": "C#",
        ".cpp": "C++",
        ".cc": "C++",
        ".c": "C",
        ".h": "C",
        ".rs": "Rust",
        ".swift": "Swift",
        ".m": "Objective-C",
        ".scala": "Scala",
        ".sh": "Shell",
        ".bash": "Shell",
    }
    
    # Directories to ignore during scanning
    IGNORE_DIRS = {
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
        "vendor",
        "build",
        "dist",
        ".git",
        ".svn",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "target",  # Rust/Java
        "bin",
        "obj",
    }
    
    def detect(self, project_path: Path, min_files: int = 3) -> List[str]:
        """
        Detect programming languages in project
        
        Args:
            project_path: Path to project directory
            min_files: Minimum number of files to consider a language present
            
        Returns:
            List of detected languages, sorted by file count (descending)
        """
        logger.info(f"Detecting languages in {project_path}")
        
        language_counter = Counter()
        
        try:
            # Count files by extension
            for file_path in project_path.rglob("*"):
                # Skip ignored directories
                if any(ignored in file_path.parts for ignored in self.IGNORE_DIRS):
                    continue
                
                # Skip non-files
                if not file_path.is_file():
                    continue
                
                # Check extension
                ext = file_path.suffix.lower()
                if ext in self.EXTENSIONS:
                    language = self.EXTENSIONS[ext]
                    language_counter[language] += 1
            
            # Filter by minimum file count and sort by frequency
            detected_languages = [
                lang for lang, count in language_counter.most_common()
                if count >= min_files
            ]
            
            logger.info(f"Detected languages: {detected_languages}")
            logger.debug(f"Language file counts: {dict(language_counter)}")
            
            return detected_languages
            
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return []
