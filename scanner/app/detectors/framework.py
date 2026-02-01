"""Web framework detection"""
from pathlib import Path
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)


class FrameworkDetector:
    """Detect web frameworks by analyzing config files"""
    
    def detect(self, project_path: Path) -> Optional[str]:
        """
        Detect web framework in project
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Framework name if detected, None otherwise
        """
        logger.info(f"Detecting framework in {project_path}")
        
        try:
            # Python frameworks
            framework = self._detect_python_framework(project_path)
            if framework:
                logger.info(f"Detected framework: {framework}")
                return framework
            
            # JavaScript/TypeScript frameworks
            framework = self._detect_js_framework(project_path)
            if framework:
                logger.info(f"Detected framework: {framework}")
                return framework
            
            # PHP frameworks
            framework = self._detect_php_framework(project_path)
            if framework:
                logger.info(f"Detected framework: {framework}")
                return framework
            
            # Ruby frameworks
            framework = self._detect_ruby_framework(project_path)
            if framework:
                logger.info(f"Detected framework: {framework}")
                return framework
            
            # Java frameworks
            framework = self._detect_java_framework(project_path)
            if framework:
                logger.info(f"Detected framework: {framework}")
                return framework
            
            logger.info("No framework detected")
            return None
            
        except Exception as e:
            logger.error(f"Framework detection failed: {str(e)}")
            return None
    
    def _detect_python_framework(self, project_path: Path) -> Optional[str]:
        """Detect Python frameworks (Django, Flask, FastAPI)"""
        
        # Django
        if (project_path / "manage.py").exists():
            manage_py = (project_path / "manage.py").read_text()
            if "django" in manage_py.lower():
                return "Django"
        
        # Check requirements.txt
        req_file = project_path / "requirements.txt"
        if req_file.exists():
            requirements = req_file.read_text().lower()
            if "django" in requirements:
                return "Django"
            if "flask" in requirements:
                return "Flask"
            if "fastapi" in requirements:
                return "FastAPI"
        
        return None
    
    def _detect_js_framework(self, project_path: Path) -> Optional[str]:
        """Detect JavaScript/TypeScript frameworks (React, Next.js, Express, etc.)"""
        
        package_json = project_path / "package.json"
        if not package_json.exists():
            return None
        
        try:
            data = json.loads(package_json.read_text())
            deps = {
                **data.get("dependencies", {}),
                **data.get("devDependencies", {})
            }
            
            # Next.js
            if "next" in deps:
                return "Next.js"
            
            # React (standalone)
            if "react" in deps and "next" not in deps:
                return "React"
            
            # Vue
            if "vue" in deps:
                return "Vue.js"
            
            # Angular
            if "@angular/core" in deps:
                return "Angular"
            
            # Express (backend)
            if "express" in deps:
                return "Express.js"
            
            # Nest.js
            if "@nestjs/core" in deps:
                return "NestJS"
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse package.json")
        
        return None
    
    def _detect_php_framework(self, project_path: Path) -> Optional[str]:
        """Detect PHP frameworks (Laravel, Symfony, CodeIgniter)"""
        
        # Laravel
        if (project_path / "artisan").exists():
            return "Laravel"
        
        # Composer.json
        composer_json = project_path / "composer.json"
        if composer_json.exists():
            try:
                data = json.loads(composer_json.read_text())
                require = data.get("require", {})
                
                if "laravel/framework" in require:
                    return "Laravel"
                if "symfony/symfony" in require or "symfony/framework-bundle" in require:
                    return "Symfony"
                if "codeigniter/framework" in require:
                    return "CodeIgniter"
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse composer.json")
        
        return None
    
    def _detect_ruby_framework(self, project_path: Path) -> Optional[str]:
        """Detect Ruby frameworks (Rails, Sinatra)"""
        
        gemfile = project_path / "Gemfile"
        if not gemfile.exists():
            return None
        
        try:
            content = gemfile.read_text().lower()
            if "rails" in content:
                return "Ruby on Rails"
            if "sinatra" in content:
                return "Sinatra"
        except:
            pass
        
        return None
    
    def _detect_java_framework(self, project_path: Path) -> Optional[str]:
        """Detect Java frameworks (Spring Boot, Quarkus)"""
        
        # Maven (pom.xml)
        pom_xml = project_path / "pom.xml"
        if pom_xml.exists():
            try:
                content = pom_xml.read_text()
                if "spring-boot" in content.lower():
                    return "Spring Boot"
                if "quarkus" in content.lower():
                    return "Quarkus"
            except:
                pass
        
        # Gradle (build.gradle)
        build_gradle = project_path / "build.gradle"
        if build_gradle.exists():
            try:
                content = build_gradle.read_text()
                if "spring-boot" in content.lower():
                    return "Spring Boot"
                if "quarkus" in content.lower():
                    return "Quarkus"
            except:
                pass
        
        return None
