import os
import sys

# Add current path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from services.auth import auth # this initializes firebase admin
from services.firestore import firestore_service

try:
    print("Testing connection...")
    docs = firestore_service.get_user_documents("Vm7x85AivmcZm1I2yt9jIhxkQGu2")
    print(f"Connection SUCCESS. Found {len(docs)} docs.")
except Exception as e:
    print(f"FAILED: {e}")
