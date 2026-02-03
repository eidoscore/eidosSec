import sys
import os
from pathlib import Path

# Add current dir to path
sys.path.append(os.getcwd())

print("Attempting to import modules...")

try:
    print("Importing app.orchestrator...")
    from app import orchestrator
    print("SUCCESS: app.orchestrator")
except Exception as e:
    print(f"FAILED: app.orchestrator: {e}")

try:
    print("Importing app.tools.codeql...")
    from app.tools import codeql
    print("SUCCESS: app.tools.codeql")
except Exception as e:
    print(f"FAILED: app.tools.codeql: {e}")

try:
    print("Importing app.tools.gosec...")
    from app.tools import gosec
    print("SUCCESS: app.tools.gosec")
except Exception as e:
    print(f"FAILED: app.tools.gosec: {e}")

try:
    print("Importing app.tools.sast.staticcheck...")
    from app.tools.sast import staticcheck
    print("SUCCESS: app.tools.sast.staticcheck")
except Exception as e:
    print(f"FAILED: app.tools.sast.staticcheck: {e}")

try:
    print("Importing app.tools.sast.spotbugs...")
    from app.tools.sast import spotbugs
    print("SUCCESS: app.tools.sast.spotbugs")
except Exception as e:
    print(f"FAILED: app.tools.sast.spotbugs: {e}")

try:
    print("Importing app.tools.sast.pmd...")
    from app.tools.sast import pmd
    print("SUCCESS: app.tools.sast.pmd")
except Exception as e:
    print(f"FAILED: app.tools.sast.pmd: {e}")

try:
    print("Importing app.tools.sast.shellcheck...")
    from app.tools.sast import shellcheck
    print("SUCCESS: app.tools.sast.shellcheck")
except Exception as e:
    print(f"FAILED: app.tools.sast.shellcheck: {e}")

try:
    print("Importing app.tools.sca.retirejs...")
    from app.tools.sca import retirejs
    print("SUCCESS: app.tools.sca.retirejs")
except Exception as e:
    print(f"FAILED: app.tools.sca.retirejs: {e}")

try:
    print("Importing app.tools.iac.kics...")
    from app.tools.iac import kics
    print("SUCCESS: app.tools.iac.kics")
except Exception as e:
    print(f"FAILED: app.tools.iac.kics: {e}")

try:
    print("Importing app.parsers.sarif...")
    from app.parsers import sarif
    print("SUCCESS: app.parsers.sarif")
except Exception as e:
    print(f"FAILED: app.parsers.sarif: {e}")

try:
    print("Importing app.services.license...")
    from app.services import license
    print("SUCCESS: app.services.license")
except Exception as e:
    print(f"FAILED: app.services.license: {e}")
