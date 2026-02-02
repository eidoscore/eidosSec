"""
Project language and framework detection service.

Detects programming languages and frameworks by analyzing:
1. File extensions
2. Configuration files (package.json, requirements.txt, composer.json, etc.)
3. Framework-specific files (manage.py, artisan, etc.)
"""
import os
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from collections import Counter

# File extension to language mapping
EXTENSION_TO_LANGUAGE = {
    # Python
    '.py': 'Python',
    '.pyx': 'Python',
    '.pyw': 'Python',

    # JavaScript/TypeScript
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.mjs': 'JavaScript',
    '.cjs': 'JavaScript',

    # PHP
    '.php': 'PHP',
    '.phtml': 'PHP',
    '.php3': 'PHP',
    '.php4': 'PHP',
    '.php5': 'PHP',

    # Ruby
    '.rb': 'Ruby',
    '.erb': 'Ruby',
    '.rake': 'Ruby',

    # Java/Kotlin
    '.java': 'Java',
    '.kt': 'Kotlin',
    '.kts': 'Kotlin',

    # C/C++
    '.c': 'C',
    '.h': 'C',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.hpp': 'C++',
    '.hxx': 'C++',

    # C#
    '.cs': 'C#',

    # Go
    '.go': 'Go',

    # Rust
    '.rs': 'Rust',

    # Swift
    '.swift': 'Swift',

    # Scala
    '.scala': 'Scala',

    # Shell
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.zsh': 'Shell',

    # Other
    '.r': 'R',
    '.R': 'R',
    '.pl': 'Perl',
    '.pm': 'Perl',
    '.lua': 'Lua',
    '.dart': 'Dart',
    '.ex': 'Elixir',
    '.exs': 'Elixir',
    '.erl': 'Erlang',
    '.hrl': 'Erlang',
    '.hs': 'Haskell',
    '.clj': 'Clojure',
    '.cljs': 'Clojure',
    '.vue': 'Vue',
    '.svelte': 'Svelte',
}

# Framework detection rules
# Each rule is: (file_or_pattern, framework_name, languages)
FRAMEWORK_RULES = [
    # Python Frameworks
    ('manage.py', 'Django', ['Python']),
    ('django/', 'Django', ['Python']),
    ('settings.py', 'Django', ['Python']),
    ('flask_app.py', 'Flask', ['Python']),
    ('app.py', 'Flask', ['Python']),  # Common Flask pattern
    ('fastapi', 'FastAPI', ['Python']),
    ('main.py', 'FastAPI', ['Python']),  # Common FastAPI pattern
    ('requirements.txt', None, ['Python']),  # Just indicates Python
    ('pyproject.toml', None, ['Python']),
    ('setup.py', None, ['Python']),
    ('Pipfile', None, ['Python']),

    # JavaScript/Node Frameworks
    ('package.json', None, ['JavaScript']),
    ('next.config.js', 'Next.js', ['JavaScript', 'TypeScript']),
    ('next.config.mjs', 'Next.js', ['JavaScript', 'TypeScript']),
    ('nuxt.config.js', 'Nuxt.js', ['JavaScript', 'TypeScript']),
    ('nuxt.config.ts', 'Nuxt.js', ['JavaScript', 'TypeScript']),
    ('angular.json', 'Angular', ['TypeScript']),
    ('vue.config.js', 'Vue.js', ['JavaScript', 'TypeScript']),
    ('vite.config.js', 'Vite', ['JavaScript', 'TypeScript']),
    ('vite.config.ts', 'Vite', ['JavaScript', 'TypeScript']),
    ('svelte.config.js', 'Svelte', ['JavaScript', 'TypeScript']),
    ('gatsby-config.js', 'Gatsby', ['JavaScript']),
    ('remix.config.js', 'Remix', ['JavaScript', 'TypeScript']),
    ('express', 'Express.js', ['JavaScript', 'TypeScript']),
    ('nest-cli.json', 'NestJS', ['TypeScript']),

    # PHP Frameworks
    ('artisan', 'Laravel', ['PHP']),
    ('composer.json', None, ['PHP']),
    ('symfony.lock', 'Symfony', ['PHP']),
    ('wp-config.php', 'WordPress', ['PHP']),
    ('wp-content/', 'WordPress', ['PHP']),
    ('drupal/', 'Drupal', ['PHP']),
    ('craft/', 'Craft CMS', ['PHP']),

    # Ruby Frameworks
    ('Gemfile', None, ['Ruby']),
    ('Rakefile', None, ['Ruby']),
    ('config.ru', 'Ruby on Rails', ['Ruby']),
    ('rails', 'Ruby on Rails', ['Ruby']),
    ('sinatra', 'Sinatra', ['Ruby']),

    # Java Frameworks
    ('pom.xml', 'Maven', ['Java']),
    ('build.gradle', 'Gradle', ['Java', 'Kotlin']),
    ('build.gradle.kts', 'Gradle', ['Kotlin']),
    ('spring', 'Spring', ['Java']),
    ('application.properties', 'Spring Boot', ['Java']),
    ('application.yml', 'Spring Boot', ['Java']),

    # Go Frameworks
    ('go.mod', None, ['Go']),
    ('go.sum', None, ['Go']),
    ('gin', 'Gin', ['Go']),
    ('echo', 'Echo', ['Go']),
    ('fiber', 'Fiber', ['Go']),

    # Rust
    ('Cargo.toml', None, ['Rust']),
    ('Cargo.lock', None, ['Rust']),

    # .NET
    ('.csproj', '.NET', ['C#']),
    ('.sln', '.NET', ['C#']),
    ('appsettings.json', 'ASP.NET', ['C#']),

    # Mobile
    ('pubspec.yaml', 'Flutter', ['Dart']),
    ('Podfile', 'iOS', ['Swift', 'Objective-C']),
    ('AndroidManifest.xml', 'Android', ['Java', 'Kotlin']),
    ('build.gradle', 'Android', ['Java', 'Kotlin']),

    # Infrastructure
    ('Dockerfile', 'Docker', []),
    ('docker-compose.yml', 'Docker Compose', []),
    ('docker-compose.yaml', 'Docker Compose', []),
    ('terraform/', 'Terraform', []),
    ('.tf', 'Terraform', []),
    ('kubernetes/', 'Kubernetes', []),
    ('k8s/', 'Kubernetes', []),
    ('helm/', 'Helm', []),
]

# Directories to skip during analysis
SKIP_DIRS = {
    'node_modules', 'vendor', 'venv', '.venv', 'env', '.env',
    '__pycache__', '.git', '.svn', '.hg', 'dist', 'build',
    'target', 'out', 'bin', 'obj', '.idea', '.vscode',
    'coverage', '.nyc_output', '.pytest_cache', '.tox',
    'eggs', '.eggs', '*.egg-info', '.mypy_cache',
}

# Maximum files to analyze (for performance)
MAX_FILES_TO_ANALYZE = 5000
MAX_DEPTH = 10


class ProjectDetector:
    """Detects languages and frameworks in a project directory."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.files_analyzed = 0
        self.extension_counts: Counter = Counter()
        self.detected_frameworks: List[str] = []
        self.config_files_found: List[str] = []

    def detect(self) -> Dict:
        """
        Analyze the project and return detection results.

        Returns:
            Dict with keys: languages, framework, files_analyzed, detection_confidence
        """
        if not self.project_path.exists():
            return {
                'path': str(self.project_path),
                'languages': [],
                'framework': None,
                'files_analyzed': 0,
                'detection_confidence': 0.0,
                'error': 'Path does not exist'
            }

        if not self.project_path.is_dir():
            return {
                'path': str(self.project_path),
                'languages': [],
                'framework': None,
                'files_analyzed': 0,
                'detection_confidence': 0.0,
                'error': 'Path is not a directory'
            }

        # Scan directory
        self._scan_directory(self.project_path, depth=0)

        # Detect languages from extensions
        languages = self._detect_languages()

        # Detect framework from config files
        framework = self._detect_framework()

        # Calculate confidence
        confidence = self._calculate_confidence(languages, framework)

        return {
            'path': str(self.project_path),
            'languages': languages,
            'framework': framework,
            'files_analyzed': self.files_analyzed,
            'detection_confidence': confidence
        }

    def _scan_directory(self, path: Path, depth: int):
        """Recursively scan directory for files."""
        if depth > MAX_DEPTH:
            return

        if self.files_analyzed >= MAX_FILES_TO_ANALYZE:
            return

        try:
            for item in path.iterdir():
                if self.files_analyzed >= MAX_FILES_TO_ANALYZE:
                    return

                # Skip hidden files and directories
                if item.name.startswith('.') and item.name not in ['.env', '.gitignore']:
                    continue

                # Skip common non-source directories
                if item.is_dir() and item.name in SKIP_DIRS:
                    continue

                if item.is_file():
                    self._analyze_file(item)
                elif item.is_dir():
                    self._scan_directory(item, depth + 1)
        except PermissionError:
            pass  # Skip directories we can't access

    def _analyze_file(self, file_path: Path):
        """Analyze a single file."""
        self.files_analyzed += 1

        # Check extension
        ext = file_path.suffix.lower()
        if ext in EXTENSION_TO_LANGUAGE:
            self.extension_counts[ext] += 1

        # Check if it's a config file
        filename = file_path.name.lower()
        relative_path = str(file_path.relative_to(self.project_path))

        for pattern, framework, langs in FRAMEWORK_RULES:
            pattern_lower = pattern.lower()
            if filename == pattern_lower or pattern_lower in relative_path.lower():
                self.config_files_found.append(filename)
                if framework and framework not in self.detected_frameworks:
                    self.detected_frameworks.append(framework)

    def _detect_languages(self) -> List[str]:
        """Determine primary languages from extension counts."""
        if not self.extension_counts:
            return []

        # Convert extensions to languages
        language_counts: Counter = Counter()
        for ext, count in self.extension_counts.items():
            lang = EXTENSION_TO_LANGUAGE.get(ext)
            if lang:
                language_counts[lang] += count

        if not language_counts:
            return []

        # Return top languages (those with at least 5% of the most common)
        max_count = language_counts.most_common(1)[0][1]
        threshold = max_count * 0.05  # 5% threshold

        languages = [
            lang for lang, count in language_counts.most_common()
            if count >= threshold
        ]

        return languages[:5]  # Return top 5 languages max

    def _detect_framework(self) -> Optional[str]:
        """Determine the primary framework."""
        if not self.detected_frameworks:
            return None

        # Priority order for common frameworks
        framework_priority = [
            'Django', 'FastAPI', 'Flask',  # Python
            'Next.js', 'Nuxt.js', 'Angular', 'Vue.js', 'Express.js', 'NestJS',  # JS
            'Laravel', 'Symfony', 'WordPress',  # PHP
            'Ruby on Rails', 'Sinatra',  # Ruby
            'Spring Boot', 'Spring',  # Java
            'ASP.NET', '.NET',  # C#
            'Flutter',  # Mobile
        ]

        for framework in framework_priority:
            if framework in self.detected_frameworks:
                return framework

        # Return first detected if no priority match
        return self.detected_frameworks[0] if self.detected_frameworks else None

    def _calculate_confidence(self, languages: List[str], framework: Optional[str]) -> float:
        """Calculate detection confidence score."""
        if self.files_analyzed == 0:
            return 0.0

        confidence = 0.0

        # Base confidence from file count
        if self.files_analyzed >= 100:
            confidence += 0.3
        elif self.files_analyzed >= 20:
            confidence += 0.2
        elif self.files_analyzed >= 5:
            confidence += 0.1

        # Confidence from languages detected
        if len(languages) >= 1:
            confidence += 0.3
        if len(languages) >= 2:
            confidence += 0.1

        # Confidence from framework detection
        if framework:
            confidence += 0.3

        # Confidence from config files
        if len(self.config_files_found) >= 3:
            confidence += 0.1

        return min(confidence, 1.0)


def detect_project(path: str) -> Dict:
    """
    Detect languages and framework for a project.

    Args:
        path: Absolute path to the project directory

    Returns:
        Dict with detection results
    """
    detector = ProjectDetector(path)
    return detector.detect()
