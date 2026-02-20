from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import openpyxl
import xlrd
from pptx import Presentation
import csv
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
    def extract_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = DocxDocument(io.BytesIO(file_content))
            text = '\n'.join(para.text for para in doc.paragraphs if para.text.strip())
            return text.strip()
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return ""
    
    @staticmethod
    def extract_from_xlsx(file_content: bytes) -> str:
        """Extract text from XLSX file"""
        try:
            wb = openpyxl.load_workbook(io.BytesIO(file_content), data_only=True)
            lines = []
            for sheet in wb.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    row_text = ' | '.join(str(c) for c in row if c is not None)
                    if row_text.strip():
                        lines.append(row_text)
            return '\n'.join(lines)
        except Exception as e:
            print(f"Error extracting XLSX text: {e}")
            return ""
    
    @staticmethod
    def extract_from_xls(file_content: bytes) -> str:
        """Extract text from legacy XLS file"""
        try:
            wb = xlrd.open_workbook(file_contents=file_content)
            lines = []
            for sheet in wb.sheets():
                for row_idx in range(sheet.nrows):
                    row_text = ' | '.join(str(sheet.cell_value(row_idx, c)) for c in range(sheet.ncols))
                    if row_text.strip():
                        lines.append(row_text)
            return '\n'.join(lines)
        except Exception as e:
            print(f"Error extracting XLS text: {e}")
            return ""
    
    @staticmethod
    def extract_from_csv(file_content: bytes) -> str:
        """Extract text from CSV file"""
        try:
            text = file_content.decode('utf-8', errors='replace')
            reader = csv.reader(io.StringIO(text))
            lines = [' | '.join(row) for row in reader if any(cell.strip() for cell in row)]
            return '\n'.join(lines)
        except Exception as e:
            print(f"Error extracting CSV text: {e}")
            return ""
    
    @staticmethod
    def extract_from_pptx(file_content: bytes) -> str:
        """Extract text from PPTX file"""
        try:
            prs = Presentation(io.BytesIO(file_content))
            lines = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, 'text') and shape.text.strip():
                        lines.append(shape.text)
            return '\n'.join(lines)
        except Exception as e:
            print(f"Error extracting PPTX text: {e}")
            return ""
    
    @staticmethod
    def extract_text(file_content: bytes, file_extension: str) -> str:
        """
        Extract text based on file extension
        Supports: .pdf, .txt, .md, .docx, .doc, .xlsx, .xls, .csv, .pptx, .ppt
        """
        ext = file_extension.lower()
        
        if ext == '.pdf':
            return TextExtractor.extract_from_pdf(file_content)
        elif ext in ('.txt', '.md'):
            return TextExtractor.extract_from_text(file_content)
        elif ext in ('.docx', '.doc'):
            return TextExtractor.extract_from_docx(file_content)
        elif ext == '.xlsx':
            return TextExtractor.extract_from_xlsx(file_content)
        elif ext == '.xls':
            return TextExtractor.extract_from_xls(file_content)
        elif ext == '.csv':
            return TextExtractor.extract_from_csv(file_content)
        elif ext in ('.pptx', '.ppt'):
            return TextExtractor.extract_from_pptx(file_content)
        else:
            return ""

# Singleton instance
text_extractor = TextExtractor()
