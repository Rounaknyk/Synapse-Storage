from PyPDF2 import PdfReader
import io

class TextExtractor:
    @staticmethod
    def extract_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    @staticmethod
    def extract_from_text(file_content: bytes) -> str:
        """Extract text from TXT or MD file"""
        try:
            return file_content.decode('utf-8').strip()
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    @staticmethod
    def extract_text(file_content: bytes, file_extension: str) -> str:
        """
        Extract text based on file extension
        Supports: .pdf, .txt, .md
        """
        file_extension = file_extension.lower()
        
        if file_extension == '.pdf':
            return TextExtractor.extract_from_pdf(file_content)
        elif file_extension in ['.txt', '.md']:
            return TextExtractor.extract_from_text(file_content)
        else:
            return ""

# Singleton instance
text_extractor = TextExtractor()
