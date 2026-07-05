from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
POPPLER_PATH = r"C:\Program Files\poppler\poppler-26.02.0\Library\bin"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

last_txt_filename = None  # track most recent output for /download


def preprocess_image(pil_image):
    """Grayscale, upscale, denoise, adaptive threshold.
    Takes/returns PIL image so both jpg/png and pdf-page branches can reuse it."""
    img = np.array(pil_image.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # upscale 2x -- helps small/code-block text
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # denoise
    gray = cv2.fastNlMeansDenoising(gray, h=30)

    # adaptive threshold -- handles uneven lighting/screenshots better than global
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 2
    )

    return Image.fromarray(thresh)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    global last_txt_filename

    file = request.files.get("file")

    if not file or file.filename == "":
        return "No file selected", 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    allowed_ext = {"jpg", "jpeg", "png", "pdf"}
    if ext not in allowed_ext:
        return "Unsupported file type", 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    if ext in {"jpg", "jpeg", "png"}:
        image = Image.open(filepath).convert("RGB")
        try:
            processed = preprocess_image(image)
            extracted_text = pytesseract.image_to_string(
                processed,
                config="--oem 3 --psm 6"
            )
        except Exception as e:
            extracted_text = f"OCR Error: {e}"

    elif ext == "pdf":
        try:
            pages = convert_from_path(
                filepath,
                poppler_path=POPPLER_PATH
            )
            page_texts = []
            for page_num, page_image in enumerate(pages, start=1):
                processed = preprocess_image(page_image)
                page_text = pytesseract.image_to_string(
                    processed,
                    config="--oem 3 --psm 6"
                )
                page_texts.append(f"--- Page {page_num} ---\n{page_text}")
            extracted_text = "\n\n".join(page_texts)
        except Exception as e:
            extracted_text = f"OCR Error: {e}"

    # dynamic output filename, tied to source file
    txt_filename = os.path.splitext(filename)[0] + ".txt"
    output_path = os.path.join(OUTPUT_FOLDER, txt_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    last_txt_filename = txt_filename

    return render_template("index.html", extracted_text=extracted_text)


@app.route("/download")
def download():
    if not last_txt_filename:
        return "No OCR output available.", 404

    output_path = os.path.join(OUTPUT_FOLDER, last_txt_filename)

    if not os.path.exists(output_path):
        return "No OCR output available.", 404

    return send_file(
        output_path,
        as_attachment=True,
        download_name=last_txt_filename
    )


if __name__ == "__main__":
    app.run(debug=True)