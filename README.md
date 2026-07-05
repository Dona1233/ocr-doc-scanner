# OCR Document Scanner

## Overview
Web app that extracts text from uploaded images (JPG/PNG) and PDFs using OCR (Tesseract). User uploads a file, backend runs OCR, extracted text shown in browser and available for download as `.txt`. Optional AI summary step (Gemini API) turns raw OCR output into key points, dates, and action items.

## Features
- Upload image (JPG/PNG)
- Upload PDF (multi-page supported)
- Extract text via Tesseract OCR
- Display extracted text in browser
- Download extracted text as `.txt`
- (Optional) AI-generated summary of extracted text via Gemini API

## Tech Stack
**Backend:** Python, Flask
**OCR:** Tesseract OCR, pytesseract
**Image Processing:** Pillow, OpenCV (optional preprocessing)
**PDF Handling:** pdf2image
**Frontend:** HTML, CSS, Bootstrap

## Installation

1. Clone repo
   ```
   git clone <repo-url>
   cd ocr-document-scanner
   ```

2. Create and activate virtual environment
   ```
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Install Tesseract OCR engine (separate from Python packages)
   - **Windows:** download from https://github.com/UB-Mannheim/tesseract/wiki, then set path in code:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
     ```
   - **Linux:** `sudo apt install tesseract-ocr`
   - **Mac:** `brew install tesseract`

5. Run the app
   ```
   python app.py
   ```
   Visit `http://127.0.0.1:5000` in browser.

## Screenshots
*(add after UI is built — e.g. upload screen, extracted text view, download button)*

## Future Improvements
- Drag & drop upload with progress spinner
- Image preprocessing pipeline (grayscale → threshold → denoise) for better accuracy on scanned/noisy docs
- Support for handwritten text recognition
- Batch upload / multi-file processing
- Export extracted text as `.docx` or `.pdf` in addition to `.txt`
- User authentication + history of past scans