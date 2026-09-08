import streamlit as st
import fitz  # PyMuPDF
import re
import os
import shutil
import tempfile
from PIL import Image
import io
import base64
from datetime import datetime

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    TESSERACT_AVAILABLE = False

# Use the standard Windows installation when Tesseract is not on PATH.
if os.name == "nt" and not shutil.which("tesseract"):
    windows_tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if TESSERACT_AVAILABLE and os.path.isfile(windows_tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = windows_tesseract_path

# Configure page
st.set_page_config(
    page_title="Document Intelligence MVP",
    page_icon="📄",
    layout="wide"
)

# Title and description
st.title("📄 AI Document Intelligence & Workflow Platform")
st.markdown("Upload a PDF, JPG, or PNG to extract information automatically.")
st.markdown("---")

# Allowed file types
ALLOWED_TYPES = ["pdf", "jpg", "jpeg", "png"]

def is_allowed_file(filename):
    """Check if file type is allowed."""
    ext = filename.split(".")[-1].lower()
    return ext in ALLOWED_TYPES

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF using PyMuPDF."""
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Extract text using PyMuPDF
        doc = fitz.open(tmp_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return text if text.strip() else None
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def extract_text_from_image(uploaded_file):
    """Extract text from image using Tesseract OCR."""
    try:
        if not TESSERACT_AVAILABLE:
            st.error("OCR is unavailable because pytesseract is not installed.")
            return None
        image = Image.open(io.BytesIO(uploaded_file.getvalue()))
        text = pytesseract.image_to_string(image)
        return text if text.strip() else None
    except Exception as e:
        st.error(f"Error reading image: {e}")
        return None

def classify_document(text):
    """Classify document type using keyword-based rules."""
    text_lower = text.lower()
    
    # Invoice keywords
    invoice_keywords = ["invoice", "total", "invoice number", "bill to", "amount due", 
                        "subtotal", "tax", "payment", "due date"]
    invoice_score = sum(1 for keyword in invoice_keywords if keyword in text_lower)
    
    # Resume keywords
    resume_keywords = ["resume", "skills", "education", "experience", "curriculum vitae",
                       "cv", "work experience", "professional summary", "certifications"]
    resume_score = sum(1 for keyword in resume_keywords if keyword in text_lower)
    
    # Classification
    if invoice_score > resume_score and invoice_score >= 2:
        return "Invoice", invoice_score
    elif resume_score > invoice_score and resume_score >= 2:
        return "Resume", resume_score
    else:
        return "Other", max(invoice_score, resume_score)

def extract_invoice_info(text):
    """Extract invoice information using regex patterns."""
    info = {
        "Invoice Number": None,
        "Date": None,
        "Company Name": None,
        "Total Amount": None
    }
    
    # Invoice Number patterns
    patterns_inv_no = [
        r'[Ii]nvoice\s*(?:No|Number|#)?\s*[:.]?\s*([A-Z0-9\-]+)',
        r'[Ii][Nn][Vv](?:-|\s)*([A-Z0-9\-]+)',
        r'#[A-Z0-9]+'
    ]
    for pattern in patterns_inv_no:
        match = re.search(pattern, text)
        if match:
            info["Invoice Number"] = match.group(1) if match.groups() else match.group(0)
            break
    
    # Date patterns
    date_patterns = [
        r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
        r'[A-Za-z]+\s+\d{1,2},?\s+\d{4}'
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            info["Date"] = matches[0]
            break
    
    # Company Name patterns
    company_patterns = [
        r'[Cc]ompany\s*[:.]?\s*([A-Za-z\s&\.,]+)',
        r'[Bb]ill\s*[Tt]o\s*[:.]?\s*([A-Za-z\s&\.,]+)',
        r'[Ff]rom\s*[:.]?\s*([A-Za-z\s&\.,]+)'
    ]
    for pattern in company_patterns:
        match = re.search(pattern, text)
        if match:
            info["Company Name"] = match.group(1).strip()
            break
    
    # Total Amount patterns
    total_patterns = [
        r'[Tt]otal\s*[:.]?\s*([\$€£PKR]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        r'[Gg]rand\s*[Tt]otal\s*[:.]?\s*([\$€£PKR]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        r'[Aa]mount\s*[Dd]ue\s*[:.]?\s*([\$€£PKR]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
    ]
    for pattern in total_patterns:
        match = re.search(pattern, text)
        if match:
            info["Total Amount"] = match.group(1).strip()
            break
    
    # Filter out None values
    return {k: v for k, v in info.items() if v is not None}

def extract_resume_info(text):
    """Extract resume information using regex patterns."""
    info = {
        "Name": None,
        "Email": None,
        "Phone": None,
        "Skills": None
    }
    
    # Name patterns (typically at the beginning of resume)
    lines = text.split('\n')
    for line in lines[:20]:  # Check first 20 lines
        line = line.strip()
        if line and not any(keyword in line.lower() for keyword in 
                           ['resume', 'curriculum', 'vitae', 'cv', 'education', 'experience', 
                            'skills', 'objective', 'summary']):
            if len(line.split()) <= 4:  # Name is usually short
                info["Name"] = line
                break
    
    # Email pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, text)
    if email_match:
        info["Email"] = email_match.group(0)
    
    # Phone patterns (US/Pakistan format)
    phone_patterns = [
        r'\+?\d{2}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}'
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            info["Phone"] = match.group(0)
            break
    
    # Skills section
    skills_section = re.search(r'(?:Skills|Technical Skills|Core Competencies)[\s:]*([^.,]+(?:, [^.,]+)*)', 
                               text, re.IGNORECASE)
    if skills_section:
        skills = skills_section.group(1).strip()
        # Clean up the skills
        skills = re.sub(r'\s+', ' ', skills)
        info["Skills"] = skills
    
    # Filter out None values
    return {k: v for k, v in info.items() if v is not None}

def process_document(uploaded_file):
    """Main processing function."""
    # Get file info
    file_name = uploaded_file.name
    file_size = uploaded_file.size
    file_ext = file_name.split(".")[-1].lower()
    file_uploaded_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Read text based on file type
    if file_ext == "pdf":
        st.info("📖 Reading text from PDF using PyMuPDF...")
        text = extract_text_from_pdf(uploaded_file)
        if text is None:
            st.warning("⚠️ No selectable text found in PDF. Trying OCR...")
            text = extract_text_from_image(uploaded_file)
    else:
        st.info("🖼️ Reading text from image using OCR...")
        text = extract_text_from_image(uploaded_file)
    
    if text is None:
        return None, None, None, None, None
    
    # Clean text
    text = ' '.join(text.split())
    
    # Classify document
    doc_type, confidence = classify_document(text)
    
    # Extract information based on document type
    if doc_type == "Invoice":
        extracted_info = extract_invoice_info(text)
    elif doc_type == "Resume":
        extracted_info = extract_resume_info(text)
    else:
        extracted_info = {}
    
    return text, doc_type, confidence, extracted_info, {
        "file_name": file_name,
        "file_size": file_size,
        "file_type": file_ext,
        "uploaded": file_uploaded_time
    }

# File uploader
uploaded_file = st.file_uploader(
    "📤 Choose a document to upload",
    type=ALLOWED_TYPES,
    help="Supported formats: PDF, JPG, JPEG, PNG"
)

if uploaded_file is not None:
    # Display file info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 Filename", uploaded_file.name)
    with col2:
        file_size_kb = uploaded_file.size / 1024
        st.metric("📦 File Size", f"{file_size_kb:.2f} KB")
    with col3:
        file_type = uploaded_file.name.split(".")[-1].upper()
        st.metric("📁 File Type", file_type)
    
    # Process document
    with st.spinner("🔄 Processing document..."):
        text, doc_type, confidence, extracted_info, file_info = process_document(uploaded_file)
    
    if text:
        # Display results
        st.markdown("---")
        st.subheader("📊 Document Analysis Results")
        
        # Result columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Document Information")
            st.write(f"**Document Type:** {doc_type}")
            if confidence > 0:
                st.write(f"**Confidence Score:** {confidence}/10")
            st.write(f"**Character Count:** {len(text):,}")
            st.write(f"**Word Count:** {len(text.split()):,}")
        
        with col2:
            st.markdown("### 🔍 Extracted Information")
            if extracted_info:
                for key, value in extracted_info.items():
                    st.write(f"**{key}:** {value}")
            else:
                st.info("ℹ️ No specific fields could be extracted from this document.")
        
        # Full extracted text
        st.markdown("---")
        st.subheader("📜 Extracted Text")
        st.text_area("Full Text Content", text, height=200)
        
        # File Preview
        if file_type.lower() in ["jpg", "jpeg", "png"]:
            st.markdown("---")
            st.subheader("🖼️ Image Preview")
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        # Download extracted text
        st.markdown("---")
        st.download_button(
            label="📥 Download Extracted Text",
            data=text,
            file_name=f"{uploaded_file.name}_extracted.txt",
            mime="text/plain"
        )
        
    else:
        st.error("❌ Failed to extract text from the document. Please try another file.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>Made with ❤️ for ZYROO Internship Program</p>
    <p>
        <a href="https://zyroo.org" target="_blank">Website</a> | 
        <a href="https://zyroo.org/internships" target="_blank">Internships</a> | 
        <a href="https://www.linkedin.com/company/zyr0-co/" target="_blank">LinkedIn</a>
    </p>
</div>
""", unsafe_allow_html=True)