import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Request, HTTPException
from config import settings

# Initialize Firebase Admin SDK
try:
    if settings.FIREBASE_CREDENTIALS_BASE64:
        # Decode base64 string to JSON dict
        cred_json = base64.b64decode(settings.FIREBASE_CREDENTIALS_BASE64).decode('utf-8')
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("✓ Firebase Admin initialized via BASE64 Environment Variable")
    elif os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        print(f"✓ Firebase Admin initialized via {settings.FIREBASE_CREDENTIALS_PATH}")
    else:
        # For local development if no key is provided, we can either:
        # 1. Raise an error
        # 2. Mock authentication (less secure but easier to run)
        print(f"⚠️  WARNING: Firebase credentials file not found at '{settings.FIREBASE_CREDENTIALS_PATH}'.")
        print("          If you don't provide a valid token from frontend, endpoints will fail.")
        # We try to initialize without credentials which may work if GOOGLE_APPLICATION_CREDENTIALS is set
        firebase_admin.initialize_app()
except Exception as e:
    print(f"⚠️  Firebase Admin initialization issue: {e}")

async def get_current_user(request: Request) -> dict:
    """FastAPI Dependency to enforce valid Firebase Auth tokens."""
    auth_header = request.headers.get("Authorization")
    
    # Check if header exists and is Bearer
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = auth_header.split(" ")[1]
    
    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
