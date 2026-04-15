from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = "data"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Landing Page Route
@app.route("/")
def home():
    return render_template("index.html")

# Upload CSV file page
@app.route("/upload")
def upload_page():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]

    if file.filename == "":
        return "No file selected"
    
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(save_path)

    return f"File upload successfully: {file.filename}"

# --------
# Run App
# --------

if __name__ == "__main__":
    app.run(debug=True)
