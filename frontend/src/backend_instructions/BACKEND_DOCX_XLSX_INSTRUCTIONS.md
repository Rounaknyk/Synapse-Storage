# 🔧 Backend Instructions — DOCX / XLSX / CSV / PPTX Support

The frontend now accepts these additional file types. The backend must be updated to:
1. Allow them past the extension validation gate
2. Extract text from each format

---

## 1 · Allowed Extensions — `main.py`

In `upload_file`, change the extension whitelist:

```python
# BEFORE
if file_extension not in ['.pdf', '.txt', '.md']:

# AFTER
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md', '.docx', '.doc', '.xlsx', '.xls', '.csv', '.pptx', '.ppt'}
if file_extension not in ALLOWED_EXTENSIONS:
```

---

## 2 · New Python Dependencies — `requirements.txt`

Add these lines:

```txt
python-docx>=1.1.0       # .docx / .doc text extraction
openpyxl>=3.1.2          # .xlsx text extraction
xlrd>=2.0.1              # .xls (legacy Excel)
python-pptx>=1.0.2       # .pptx / .ppt text extraction
```

Install inside the venv:
```bash
source venv/bin/activate
pip install python-docx openpyxl xlrd python-pptx
pip freeze > requirements.txt
```

---

## 3 · Text Extractor — `utils/text_extractor.py`

Add extraction methods for each new format:

```python
# At the top, add imports:
from docx import Document as DocxDocument
import openpyxl
import xlrd
from pptx import Presentation
import csv
import io

# Inside TextExtractor class, add these methods:

def _extract_docx(self, content: bytes) -> str:
    doc = DocxDocument(io.BytesIO(content))
    return '\n'.join(para.text for para in doc.paragraphs if para.text.strip())

def _extract_xlsx(self, content: bytes) -> str:
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
    lines = []
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(values_only=True):
            row_text = ' | '.join(str(c) for c in row if c is not None)
            if row_text.strip():
                lines.append(row_text)
    return '\n'.join(lines)

def _extract_xls(self, content: bytes) -> str:
    wb = xlrd.open_workbook(file_contents=content)
    lines = []
    for sheet in wb.sheets():
        for row_idx in range(sheet.nrows):
            row_text = ' | '.join(str(sheet.cell_value(row_idx, c)) for c in range(sheet.ncols))
            if row_text.strip():
                lines.append(row_text)
    return '\n'.join(lines)

def _extract_csv(self, content: bytes) -> str:
    text = content.decode('utf-8', errors='replace')
    reader = csv.reader(io.StringIO(text))
    return '\n'.join(' | '.join(row) for row in reader if any(cell.strip() for cell in row))

def _extract_pptx(self, content: bytes) -> str:
    prs = Presentation(io.BytesIO(content))
    lines = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, 'text') and shape.text.strip():
                lines.append(shape.text)
    return '\n'.join(lines)
```

Then update the dispatcher in `extract_text()`:

```python
def extract_text(self, content: bytes, extension: str) -> str:
    ext = extension.lower()
    if ext == '.pdf':
        return self._extract_pdf(content)
    elif ext in ('.txt', '.md'):
        return content.decode('utf-8', errors='replace')
    elif ext in ('.docx', '.doc'):
        return self._extract_docx(content)
    elif ext == '.xlsx':
        return self._extract_xlsx(content)
    elif ext == '.xls':
        return self._extract_xls(content)
    elif ext == '.csv':
        return self._extract_csv(content)
    elif ext in ('.pptx', '.ppt'):
        return self._extract_pptx(content)
    else:
        return ""
```

---

## 4 · Content-Type Mapping (optional, for MinIO uploads)

If you set a content type when uploading to MinIO, map the new extensions:

```python
CONTENT_TYPES = {
    '.pdf':  'application/pdf',
    '.txt':  'text/plain',
    '.md':   'text/markdown',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.doc':  'application/msword',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls':  'application/vnd.ms-excel',
    '.csv':  'text/csv',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.ppt':  'application/vnd.ms-powerpoint',
}
content_type = CONTENT_TYPES.get(file_extension, 'application/octet-stream')
```

---

## 5 · Testing Checklist

- [ ] Upload a `.docx` → classified, text extracted, stored
- [ ] Upload a `.xlsx` → rows readable, classified
- [ ] Upload a `.csv` → rows readable, classified
- [ ] Upload a `.pptx` → slide text extracted, classified
- [ ] Unsupported type (e.g. `.zip`) → 400 error returned
- [ ] Search "revenue" → finds the uploaded Excel/Word doc
