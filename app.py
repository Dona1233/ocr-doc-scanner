from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
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
            extracted_text = pytesseract.image_to_string(image)
        except Exception as e:
            extracted_text = f"OCR Error: {e}"
    elif ext == "pdf":
        extracted_text = ""  # handled separately, Step 10

    txt_filename = os.path.splitext(filename)[0] + ".txt"
    output_path = os.path.join(OUTPUT_FOLDER, txt_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return render_template("index.html", extracted_text=extracted_text, txt_filename=txt_filename)

@app.route("/download/<txt_filename>")
def download(txt_filename):
    output_path = os.path.join(OUTPUT_FOLDER, secure_filename(txt_filename))

    if not os.path.exists(output_path):
        return "No OCR output available.", 404

    return send_file(output_path, as_attachment=True, download_name=txt_filename)

if __name__ == "__main__":
    app.run(debug=True)