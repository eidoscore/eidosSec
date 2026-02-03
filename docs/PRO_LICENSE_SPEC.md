# eidosSec PRO Tier - License Key Enforcement Specification

**Status:** Design Phase (Month 4 prep for Month 5/6 implementation)
**Target:** PRO tier launch with $39/month pricing

---

## 1. Overview

### Business Requirements
- FREE tier: 15 tools, 3 projects, 1 user, 10 scan history
- PRO tier: All features unlocked for $39/month per account (unlimited users)
- License validation must work offline (local Docker deployment)
- Grace period for expired licenses (7 days)

### Technical Requirements
- JWT-based license keys (self-contained, offline-verifiable)
- License stored in PostgreSQL `settings` table
- Frontend feature gating based on license tier
- Backend enforcement for API rate limits and feature access

---

## 2. License Key Format

### JWT Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "iss": "eidossec.com",
    "sub": "license",
    "iat": 1706918400,
    "exp": 1709596800,
    "license_id": "lic_abc123def456",
    "tier": "pro",
    "account_email": "user@example.com",
    "features": {
      "max_projects": -1,
      "max_users": -1,
      "max_scans_history": -1,
      "tools": "all",
      "scan_modes": ["quick", "deep", "custom"],
      "ai_features": true,
      "export_formats": ["json", "pdf", "html", "sarif"],
      "ci_cd_templates": true,
      "compliance_reports": true,
      "team_collaboration": true
    },
    "metadata": {
      "stripe_subscription_id": "sub_xyz789",
      "created_at": "2024-02-01T00:00:00Z"
    }
  },
  "signature": "..."
}
```

### Key Properties

| Field | Description | Example |
|-------|-------------|---------|
| `iss` | Issuer (always eidossec.com) | `"eidossec.com"` |
| `sub` | Subject type | `"license"` |
| `iat` | Issued at (Unix timestamp) | `1706918400` |
| `exp` | Expiration (Unix timestamp) | `1709596800` |
| `license_id` | Unique license identifier | `"lic_abc123def456"` |
| `tier` | License tier | `"free"` or `"pro"` |
| `features` | Feature flags object | See above |

---

## 3. Cryptographic Signing

### Key Pair Generation

```bash
# Generate RSA key pair (do once, store securely)
openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

### Signing Flow (Server-side, on license.eidossec.com)

```python
import jwt
from datetime import datetime, timedelta

def generate_license(account_email: str, tier: str, duration_days: int = 30):
    payload = {
        "iss": "eidossec.com",
        "sub": "license",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=duration_days),
        "license_id": f"lic_{generate_id()}",
        "tier": tier,
        "account_email": account_email,
        "features": get_tier_features(tier),
    }

    with open("private_key.pem", "r") as f:
        private_key = f.read()

    return jwt.encode(payload, private_key, algorithm="RS256")
```

### Verification Flow (Client-side, in eidosSec backend)

```python
import jwt

# Public key is bundled with eidosSec
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhki...
-----END PUBLIC KEY-----"""

def verify_license(license_key: str) -> dict:
    try:
        payload = jwt.decode(
            license_key,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer="eidossec.com"
        )
        return {"valid": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "License expired"}
    except jwt.InvalidTokenError as e:
        return {"valid": False, "error": str(e)}
```

---

## 4. Database Schema

### Settings Table (existing)

```sql
-- License stored as JSON in settings table
INSERT INTO settings (key, value, updated_at) VALUES (
    'license',
    '{
        "key": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
        "activated_at": "2024-02-01T12:00:00Z",
        "last_verified": "2024-02-03T08:00:00Z"
    }',
    NOW()
);
```

### License Cache Table (new, for offline verification)

```sql
CREATE TABLE license_cache (
    id SERIAL PRIMARY KEY,
    license_id VARCHAR(50) UNIQUE NOT NULL,
    tier VARCHAR(20) NOT NULL,
    features JSONB NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    last_online_verify TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_license_cache_expires ON license_cache (expires_at);
```

---

## 5. Backend Implementation

### License Service (`backend/app/services/license_service.py`)

```python
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Setting
from app.config import settings
import jwt

class LicenseService:
    PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----..."""

    FREE_TIER_LIMITS = {
        "max_projects": 3,
        "max_users": 1,
        "max_scans_history": 10,
        "tools": ["semgrep", "bandit", "eslint", "phpstan", "brakeman",
                  "trufflehog", "gitleaks", "detect-secrets",
                  "trivy", "npm-audit", "pip-audit", "composer-audit",
                  "checkov", "cfn-nag", "nodejsscan"],
        "scan_modes": ["quick"],
        "ai_features": False,
        "export_formats": ["json"],
        "ci_cd_templates": False,
        "compliance_reports": False,
        "team_collaboration": False,
    }

    async def get_current_license(self, db: AsyncSession) -> dict:
        """Get and validate current license from database."""
        result = await db.execute(
            select(Setting).where(Setting.key == "license")
        )
        setting = result.scalar_one_or_none()

        if not setting:
            return {"tier": "free", "features": self.FREE_TIER_LIMITS}

        license_data = setting.value
        verification = self.verify_license(license_data.get("key", ""))

        if not verification["valid"]:
            # Check grace period (7 days after expiration)
            if verification.get("error") == "License expired":
                exp_time = self._get_expiration(license_data.get("key"))
                if exp_time and datetime.utcnow() < exp_time + timedelta(days=7):
                    return {
                        "tier": "pro",
                        "features": verification.get("payload", {}).get("features"),
                        "grace_period": True,
                        "expires_at": exp_time.isoformat()
                    }
            return {"tier": "free", "features": self.FREE_TIER_LIMITS}

        return {
            "tier": verification["payload"]["tier"],
            "features": verification["payload"]["features"],
            "expires_at": datetime.fromtimestamp(
                verification["payload"]["exp"]
            ).isoformat()
        }

    def verify_license(self, license_key: str) -> dict:
        """Verify JWT license signature and expiration."""
        try:
            payload = jwt.decode(
                license_key,
                self.PUBLIC_KEY,
                algorithms=["RS256"],
                issuer="eidossec.com"
            )
            return {"valid": True, "payload": payload}
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "License expired"}
        except jwt.InvalidTokenError as e:
            return {"valid": False, "error": str(e)}

    async def activate_license(self, db: AsyncSession, license_key: str) -> dict:
        """Activate a new license key."""
        verification = self.verify_license(license_key)

        if not verification["valid"]:
            raise ValueError(f"Invalid license: {verification['error']}")

        # Store in database
        await db.execute(
            text("""
                INSERT INTO settings (key, value, updated_at)
                VALUES ('license', :value, NOW())
                ON CONFLICT (key) DO UPDATE SET value = :value, updated_at = NOW()
            """),
            {"value": json.dumps({
                "key": license_key,
                "activated_at": datetime.utcnow().isoformat(),
                "last_verified": datetime.utcnow().isoformat()
            })}
        )
        await db.commit()

        return verification["payload"]

    async def check_feature_access(
        self, db: AsyncSession, feature: str, value: any = None
    ) -> bool:
        """Check if current license allows access to a feature."""
        license_info = await self.get_current_license(db)
        features = license_info.get("features", self.FREE_TIER_LIMITS)

        if feature not in features:
            return False

        feature_value = features[feature]

        # Boolean features
        if isinstance(feature_value, bool):
            return feature_value

        # Numeric limits (-1 = unlimited)
        if isinstance(feature_value, int):
            if feature_value == -1:
                return True
            return value is None or value < feature_value

        # List features (e.g., tools, scan_modes)
        if isinstance(feature_value, list):
            if value is None:
                return True
            if feature_value == "all":
                return True
            return value in feature_value

        return True


license_service = LicenseService()
```

### Feature Gate Dependency (`backend/app/dependencies.py`)

```python
from fastapi import Depends, HTTPException, status
from app.services.license_service import license_service

async def require_pro_feature(feature: str):
    """Dependency that checks PRO feature access."""
    async def check_access(db: AsyncSession = Depends(get_db)):
        has_access = await license_service.check_feature_access(db, feature)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"PRO subscription required for {feature}"
            )
        return True
    return check_access

# Usage in router:
@router.post("/scans/{id}/export/pdf")
async def export_pdf(
    id: str,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_pro_feature("export_formats"))
):
    # ... export logic
```

---

## 6. Frontend Implementation

### License Context (`frontend/src/contexts/LicenseContext.tsx`)

```tsx
import { createContext, useContext, useEffect, useState } from 'react'
import { api } from '@/lib/api'

interface LicenseInfo {
  tier: 'free' | 'pro'
  features: Record<string, any>
  gracePeriod?: boolean
  expiresAt?: string
}

const LicenseContext = createContext<LicenseInfo | null>(null)

export function LicenseProvider({ children }: { children: React.ReactNode }) {
  const [license, setLicense] = useState<LicenseInfo | null>(null)

  useEffect(() => {
    api.get('/license').then(res => setLicense(res.data))
  }, [])

  return (
    <LicenseContext.Provider value={license}>
      {children}
    </LicenseContext.Provider>
  )
}

export function useLicense() {
  return useContext(LicenseContext)
}

export function useFeature(feature: string): boolean {
  const license = useLicense()
  if (!license) return false

  const features = license.features
  const value = features[feature]

  if (typeof value === 'boolean') return value
  if (value === -1 || value === 'all') return true
  return !!value
}
```

### Pro Feature Gate Component

```tsx
interface ProFeatureProps {
  feature: string
  children: React.ReactNode
  fallback?: React.ReactNode
}

export function ProFeature({ feature, children, fallback }: ProFeatureProps) {
  const hasAccess = useFeature(feature)

  if (hasAccess) return <>{children}</>

  return fallback || (
    <div className="p-4 border border-dashed rounded-lg text-center">
      <Lock className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
      <p className="text-sm text-muted-foreground">
        PRO feature - <a href="/upgrade" className="text-primary">Upgrade</a>
      </p>
    </div>
  )
}

// Usage:
<ProFeature feature="ai_features">
  <Button onClick={explainWithAI}>Explain with AI</Button>
</ProFeature>
```

---

## 7. API Endpoints

### License Management Router (`backend/app/routers/license.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from app.services.license_service import license_service
from app.database import get_db

router = APIRouter()

@router.get("/")
async def get_license_info(db: AsyncSession = Depends(get_db)):
    """Get current license information."""
    return await license_service.get_current_license(db)

@router.post("/activate")
async def activate_license(
    license_key: str,
    db: AsyncSession = Depends(get_db)
):
    """Activate a new license key."""
    try:
        payload = await license_service.activate_license(db, license_key)
        return {"success": True, "tier": payload["tier"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/")
async def deactivate_license(db: AsyncSession = Depends(get_db)):
    """Remove license (revert to FREE tier)."""
    await db.execute(
        text("DELETE FROM settings WHERE key = 'license'")
    )
    await db.commit()
    return {"success": True, "tier": "free"}
```

---

## 8. Stripe Integration (High-Level)

### Webhook Handler

```python
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session["customer_email"]

        # Generate and send license key
        license_key = generate_license(email, "pro", duration_days=30)
        await send_license_email(email, license_key)

    elif event["type"] == "customer.subscription.deleted":
        # License will naturally expire, no action needed
        pass

    return {"received": True}
```

### Pricing Page Flow

```
1. User clicks "Upgrade to PRO" on /pricing
2. Frontend calls POST /api/checkout → returns Stripe Checkout URL
3. User completes payment on Stripe
4. Stripe webhook fires → generate license → email to user
5. User enters license key in Settings → activates locally
```

---

## 9. Enforcement Matrix

| Feature | FREE Limit | PRO Limit | Enforcement Location |
|---------|------------|-----------|---------------------|
| Projects | 3 | Unlimited | `POST /projects` (backend) |
| Users | 1 | Unlimited | User creation (backend) |
| Scan History | 10 | Unlimited | `GET /scans` + auto-delete (backend) |
| Tools | 15 specified | All 50+ | Tool orchestrator (scanner) |
| Scan Modes | Quick only | All modes | `POST /scans` (backend) |
| AI Features | Disabled | Enabled | AI service check (backend) |
| Export Formats | JSON only | All formats | Export endpoints (backend) |
| CI/CD Templates | Hidden | Visible | Frontend + download endpoint |
| Compliance Reports | Hidden | Enabled | Report generation (backend) |

---

## 10. Security Considerations

### License Key Security
- RSA-2048 signing (256-bit security)
- Public key bundled with app (cannot forge signatures)
- Private key stored securely on license server only
- Keys are tied to email (can revoke by blocking email)

### Anti-Piracy Measures
- License includes unique `license_id` for tracking
- Optional: periodic online verification (phone home)
- Optional: hardware fingerprinting (not recommended for Docker)

### What We DON'T Do
- No DRM that breaks offline usage
- No code obfuscation (we're open source)
- No aggressive license checks that hurt UX

**Philosophy:** Make the FREE tier useful enough that honest users convert willingly. Pirates gonna pirate - focus on value, not punishment.

---

## 11. Implementation Timeline

### Month 5 (PRO Development)
- Week 1: License key generation service
- Week 1: Backend license verification
- Week 2: Feature gating dependencies
- Week 2: Frontend license context
- Week 3: Stripe integration
- Week 3: Pricing page
- Week 4: Testing + polish

### Month 6 (Launch)
- Week 1: Soft launch to early users
- Week 2: Fix issues
- Week 3-4: Public PRO tier launch

---

*Document Version: 1.0*
*Last Updated: 2026-02-03*
