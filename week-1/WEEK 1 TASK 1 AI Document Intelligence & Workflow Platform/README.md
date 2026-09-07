# AI Document Intelligence & Workflow Platform

Document intelligence MVP developed for the ZYROO Internship Week 1 Task 01. The application lets users upload a document, extract its text, classify it, and identify useful fields automatically.

## Features

- Upload PDF, JPG, JPEG, and PNG documents
- Extract selectable PDF text with PyMuPDF
- Extract text from images and scanned PDFs with Tesseract OCR
- Classify documents as Invoice, Resume, or Other
- Extract invoice number, date, company, and total amount
- Extract resume name, email, phone number, and skills
- Review extracted text and download the result
- Use a simple Streamlit web interface

## Technology Stack

- Python
- Streamlit
- PyMuPDF
- pytesseract
- Tesseract OCR
- Pillow
- python-dotenv
- FastAPI
- Uvicorn
- python-multipart
- Regular expressions

## Requirements

- Python 3.8 or newer
- Tesseract OCR installed on the system

On Windows, install Tesseract OCR in the default location:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

The application detects this location automatically when Tesseract is not available on `PATH`.

## Setup

Open PowerShell in this project folder and create a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

`requirments.txt` is also kept as a legacy compatibility file for the original project setup.

## Run the Application

```powershell
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## FastAPI Server (Optional)

The FastAPI server provides programmatic access to the same document extraction and classification logic. It runs independently from Streamlit on port `8000`.

Start the API server:

```powershell
uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8000
```

Available URLs:

- API landing page: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

The root URL is a service status page, not the document upload interface. Use Swagger UI to upload a file interactively, or call the upload endpoint from another application.

Upload a document with PowerShell:

```powershell
curl.exe -X POST "http://localhost:8000/api/documents/upload" -F "file=@sample.pdf"
```

Upload an image with curl:

```bash
curl -X POST http://localhost:8000/api/documents/upload \
	-F "file=@sample.jpg"
```

The JSON response includes file metadata, extracted text, document type, confidence score, word and character counts, and document-specific extracted fields.

Example response shape:

```json
{
	"file": {
		"file_name": "sample.pdf",
		"file_size": 12345,
		"file_type": "pdf",
		"uploaded": "2026-09-07 10:00:00"
	},
	"document_type": "Invoice",
	"confidence_score": 4,
	"character_count": 250,
	"word_count": 42,
	"extracted_information": {},
	"extracted_text": "..."
}
```

## Run Both Servers

To start Streamlit and FastAPI together from one terminal:

```powershell
python run_both.py
```

This starts:

- Streamlit Web UI: http://localhost:8501
- FastAPI: http://localhost:8000
- FastAPI Swagger UI: http://localhost:8000/docs

Press `Ctrl+C` to stop both processes.

## Usage

### Streamlit Web UI

1. Open http://localhost:8501 in your browser.
2. Upload a PDF, JPG, JPEG, or PNG file.
3. Wait while the document is processed.
4. Review the extracted text, document type, confidence score, and detected fields.
5. Download the extracted text when needed.

### FastAPI Swagger UI

1. Open http://localhost:8000/docs.
2. Expand `POST /api/documents/upload`.
3. Select **Try it out**, choose a document, and select **Execute**.
4. Review the JSON response returned by the API.

## Project Structure

```text
.
|-- app.py
|-- fastapi_app.py
|-- requirements.txt
|-- requirments.txt
|-- run_both.py
|-- README.md
|-- venv/
```

## Notes

- Text-based PDFs are processed directly with PyMuPDF.
- Scanned PDFs and image files are processed with Tesseract OCR.
- If Tesseract is missing or unavailable, OCR-based uploads will return an error while text-based PDFs can still be processed.
- The FastAPI server duplicates the extraction functions from `app.py` as requested; the functions can be moved into a shared module in a future refactor.
- Classification and field extraction use keyword matching and regular expressions, so results may vary with document layout and image quality.