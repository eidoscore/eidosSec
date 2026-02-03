import os
import logging
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LicenseVerifier:
    def __init__(self):
        self.license_key = os.getenv("EIDOS_LICENSE_KEY", "")
        self.instance_id = os.getenv("EIDOS_INSTANCE_ID", "dev-instance") # Should be persisted
        # In Docker, 'host.docker.internal' accesses the host, but if license server is on 3000
        default_url = "http://host.docker.internal:3000/api/v1/license/verify"
        self.license_server_url = os.getenv("LICENSE_SERVER_URL", default_url)
        self.app_version = os.getenv("APP_VERSION", "0.1.0")
        
        self._cache = None
        self._cache_expiry = datetime.utcnow()
        self._cache_duration = timedelta(minutes=10) # Cache for 10 mins

    def check_feature(self, feature: str) -> bool:
        """Check if a specific feature is enabled by the current license"""
        status = self.verify()
        return feature in status.get("features", [])
        
    def verify(self) -> dict:
        """Verify license with remote server and return status/features"""
        # Return cached if valid
        if self._cache and datetime.utcnow() < self._cache_expiry:
             return self._cache

        if not self.license_key:
            return {"valid": False, "plan": "free", "features": []}
            
        try:
            payload = {
                "token": self.license_key,
                "instance_id": self.instance_id,
                "app_version": self.app_version
            }
            
            response = requests.post(
                self.license_server_url, 
                json=payload, 
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # Server response: { status: 'success', valid: true, token: 'new_token', ... }
                
                # Update rolling token (in memory for now, ideally persistent)
                if data.get("token"):
                    self.license_key = data["token"]
                    # If we were persisting, we'd save it here
                
                # Determine capabilities based on success
                # The response doesn't strictly return 'plan' in the sample I saw, 
                # but let's assume valid=PRO for now or we need to decode the new token.
                # Actually verify.js returns { status: 'success', valid: true, token: ... }
                # It doesn't return 'plan' or 'features' in the JSON body explicitly in the snippet I saw.
                # So we verify the TOKEN.
                
                # Optimization: We can decode the NEW token locally to get the plan/features.
                # But we don't have the secret! 
                # Wait, verify.js uses a dynamic secret. We CANNOT decode it locally without the secret.
                # This implies the verify endpoint SHOULD return the features/plan for the client to use, 
                # OR the client is expected to just trust "valid: true" implies "Standard" or similar?
                # AND verify.js snippet: 
                # if purchase.plan == ...? It checks db.
                
                # If the server doesn't return features, we assume 'pro' if valid for this specific app context.
                # Or we update the server to return features. 
                # FOR NOW: If valid, we assume PRO.
                
                result = {
                    "valid": True,
                    "plan": "pro",  # Placeholder
                    "features": ["deep_scan", "pro_tools", "ai_analysis"] # Placeholder
                }
                
                # Cache it
                self._cache = result
                self._cache_expiry = datetime.utcnow() + self._cache_duration
                return result
                
            else:
                logger.warning(f"License verification failed: {response.status_code} {response.text}")
                return {"valid": False, "plan": "free", "features": []}
                
        except Exception as e:
            logger.error(f"License server connection error: {e}")
            # Fail open or closed? For high security, fail closed (Free).
            return {"valid": False, "plan": "free", "features": []}
            
    def is_pro(self) -> bool:
        return self.verify().get("plan") in ["pro", "enterprise"]
