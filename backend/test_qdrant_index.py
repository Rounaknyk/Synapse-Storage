import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.qdrant_search import qdrant_search_service

qdrant_search_service.initialize_collection()
print("Qdrant collection initialized with index.")
