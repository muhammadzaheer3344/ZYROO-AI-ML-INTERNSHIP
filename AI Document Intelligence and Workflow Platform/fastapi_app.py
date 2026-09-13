import io
import os
import re
import shutil
import tempfile
from datetime import datetime

import fitz
import pytesseract
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from PIL import Image


if os.name == "nt" and not shutil.which("tesseract"):
    windows_tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.isfile(windows_tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = windows_tesseract_path


ALLOWED_TYPES = {"pdf", "jpg", "jpeg", "png"}


def is_allowed_file(filename):
    """Check if file type is allowed."""
    ext = filename.split(".")[-1].lower()
    return ext in ALLOWED_TYPES


def extract_text_from_pdf(file_content):
    """Extract text from PDF using PyMuPDF."""
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name

        doc = fitz.open(tmp_path)
        text = "".join(page.get_text() for page in doc)
        doc.close()
        return text if text.strip() else None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def extract_text_from_image(file_content):
    """Extract text from image using Tesseract OCR."""
    image = Image.open(io.BytesIO(file_content))
    text = pytesseract.image_to_string(image)
    return text if text.strip() else None


def extract_text_from_scanned_pdf(file_content):
    """Render scanned PDF pages and extract their text with Tesseract."""
    doc = fitz.open(stream=file_content, filetype="pdf")
    text = []
    for page in doc:
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        image = Image.open(io.BytesIO(pixmap.tobytes("png")))
        text.append(pytesseract.image_to_string(image))
    doc.close()
    combined_text = "\n".join(text)
    return combined_text if combined_text.strip() else None


def classify_document(text):
    """Classify document type using keyword-based rules."""
    text_lower = text.lower()
    invoice_keywords = [
        "invoice", "total", "invoice number", "bill to", "amount due",
        "subtotal", "tax", "payment", "due date"
    ]
    invoice_score = sum(1 for keyword in invoice_keywords if keyword in text_lower)

    resume_keywords = [
        "resume", "skills", "education", "experience", "curriculum vitae",
        "cv", "work experience", "professional summary", "certifications"
    ]
    resume_score = sum(1 for keyword in resume_keywords if keyword in text_lower)

    if invoice_score > resume_score and invoice_score >= 2:
        return "Invoice", invoice_score
    if resume_score > invoice_score and resume_score >= 2:
        return "Resume", resume_score
    return "Other", max(invoice_score, resume_score)


def extract_invoice_info(text):
    """Extract invoice information using regex patterns."""
    info = {
        "Invoice Number": None,
        "Date": None,
        "Company Name": None,
        "Total Amount": None,
    }

    patterns_inv_no = [
        r"[Ii]nvoice\s*(?:No|Number|#)?\s*[:.]?\s*([A-Z0-9\-]+)",
        r"[Ii][Nn][Vv](?:-|\s)*([A-Z0-9\-]+)",
        r"#[A-Z0-9]+",
    ]
    for pattern in patterns_inv_no:
        match = re.search(pattern, text)
        if match:
            info["Invoice Number"] = match.group(1) if match.groups() else match.group(0)
            break

    date_patterns = [
        r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}",
        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",
        r"[A-Za-z]+\s+\d{1,2},?\s+\d{4}",
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            info["Date"] = matches[0]
            break

    company_patterns = [
        r"[Cc]ompany\s*[:.]?\s*([A-Za-z\s&\.,]+)",
        r"[Bb]ill\s*[Tt]o\s*[:.]?\s*([A-Za-z\s&\.,]+)",
        r"[Ff]rom\s*[:.]?\s*([A-Za-z\s&\.,]+)",
    ]
    for pattern in company_patterns:
        match = re.search(pattern, text)
        if match:
            info["Company Name"] = match.group(1).strip()
            break

    total_patterns = [
        r"[Tt]otal\s*[:.]?\s*([\$€£PKR]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        r"[Gg]rand\s*[Tt]otal\s*[:.]?\s*([\$€£PKR]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        r"[Aa]mount\s*[Dd]ue\s*[:.]?\s*([\$€£PKR]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
    ]
    for pattern in total_patterns:
        match = re.search(pattern, text)
        if match:
            info["Total Amount"] = match.group(1).strip()
            break

    return {key: value for key, value in info.items() if value is not None}


def extract_resume_info(text):
    """Extract resume information using regex patterns."""
    info = {"Name": None, "Email": None, "Phone": None, "Skills": None}
    lines = text.split("\n")
    for line in lines[:20]:
        line = line.strip()
        if line and not any(keyword in line.lower() for keyword in [
            "resume", "curriculum", "vitae", "cv", "education", "experience",
            "skills", "objective", "summary",
        ]):
            if len(line.split()) <= 4:
                info["Name"] = line
                break

    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if email_match:
        info["Email"] = email_match.group(0)

    phone_patterns = [
        r"\+?\d{2}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}",
        r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}",
        r"\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}",
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            info["Phone"] = match.group(0)
            break

    skills_section = re.search(
        r"(?:Skills|Technical Skills|Core Competencies)[\s:]*([^.,]+(?:, [^.,]+)*)",
        text,
        re.IGNORECASE,
    )
    if skills_section:
        info["Skills"] = re.sub(r"\s+", " ", skills_section.group(1).strip())

    return {key: value for key, value in info.items() if value is not None}


def process_document(file_content, filename):
    """Extract and analyze an uploaded document."""
    file_ext = filename.split(".")[-1].lower()
    if file_ext == "pdf":
        text = extract_text_from_pdf(file_content)
        if text is None:
            text = extract_text_from_scanned_pdf(file_content)
    else:
        text = extract_text_from_image(file_content)

    if text is None:
        return None

    text = " ".join(text.split())
    doc_type, confidence = classify_document(text)
    extracted_info = {}
    if doc_type == "Invoice":
        extracted_info = extract_invoice_info(text)
    elif doc_type == "Resume":
        extracted_info = extract_resume_info(text)

    return {
        "file": {
            "file_name": filename,
            "file_size": len(file_content),
            "file_type": file_ext,
            "uploaded": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "document_type": doc_type,
        "confidence_score": confidence,
        "character_count": len(text),
        "word_count": len(text.split()),
        "extracted_information": extracted_info,
        "extracted_text": text,
    }


app = FastAPI(
    title="Document Intelligence API",
    description="Extract and analyze text from PDF and image documents.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document Intelligence API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 3rem; color: #1f2937; }
            main { max-width: 700px; margin: auto; }
            a { color: #2563eb; }
            code { background: #f3f4f6; padding: 0.2rem 0.4rem; }
        </style>
    </head>
    <body>
        <main>
            <h1>Document Intelligence API</h1>
            <p><strong>Document Intelligence API is running</strong></p>
            <p>Use the <a href="/docs">Swagger UI</a> to upload and analyze documents.</p>
            <p>Upload endpoint: <code>POST /api/documents/upload</code></p>
        </main>
    </body>
    </html>
    """


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or ""
    if not is_allowed_file(filename):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload a PDF, JPG, JPEG, or PNG file.",
        )

    try:
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        result = process_document(file_content, filename)
        if result is None:
            raise HTTPException(status_code=422, detail="Failed to extract text from the document.")
        return result
    except HTTPException:
        raise
    except pytesseract.TesseractNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Tesseract OCR is not installed or is not available on PATH.",
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {error}") from error