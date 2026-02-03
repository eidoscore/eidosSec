import jwt
import datetime
from cryptography.hazmat.primitives import serialization
import sys
import argparse

def issue_license(plan, customer_id, days):
    # Load private key
    try:
        with open("license_private.pem", "rb") as f:
            private_key = f.read()
    except FileNotFoundError:
        print("Error: license_private.pem not found. Run generate_keys.py first.")
        return

    # Create payload
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    payload = {
        "sub": customer_id,
        "plan": plan,
        "exp": expiry,
        "iat": datetime.datetime.utcnow(),
        "features": []
    }
    
    if plan == "pro":
        payload["features"] = ["deep_scan", "pro_tools", "ai_analysis"]
    elif plan == "enterprise":
        payload["features"] = ["deep_scan", "pro_tools", "ai_analysis", "sso", "compliance"]

    # Sign JWT
    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", default="pro", choices=["free", "pro", "enterprise"])
    parser.add_argument("--customer", default="demo_user")
    parser.add_argument("--days", type=int, default=365)
    
    args = parser.parse_args()
    
    token = issue_license(args.plan, args.customer, args.days)
    if token:
        print("\n--- LICENSE KEY ---")
        print(token)
        print("-------------------\n")
