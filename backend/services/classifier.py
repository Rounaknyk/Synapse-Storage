from config import settings

class ClassifierService:
    @staticmethod
    def classify_document(text: str) -> str:
        """
        Classify document based on keyword matching
        Returns: 'finance', 'legal', or 'general'
        """
        text_lower = text.lower()
        
        # Count keyword matches for each category
        finance_score = sum(1 for keyword in settings.CLASSIFICATION_KEYWORDS["finance"] if keyword in text_lower)
        legal_score = sum(1 for keyword in settings.CLASSIFICATION_KEYWORDS["legal"] if keyword in text_lower)
        
        # Determine category based on highest score
        if finance_score > legal_score and finance_score > 0:
            return "finance"
        elif legal_score > 0:
            return "legal"
        else:
            return "general"

# Singleton instance
classifier_service = ClassifierService()
