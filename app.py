from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

    # OCR logic goes here (Step 6-7)
    return render_template("index.html", extracted_text="placeholder")

if __name__ == "__main__":
    app.run(debug=True)