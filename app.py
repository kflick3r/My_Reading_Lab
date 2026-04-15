from flask import Flask, render_template, request
import os
import pandas as pd

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
    
    # Create folder if doesn't exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(save_path)

    return f"File upload successfully: {file.filename}"

# Analysis Page
@app.route("/analyze/<filename>")
def analyze(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    df = pd.read_csv(file_path)

    # Clean Up Goodreads CSV
    df.columns = [c.strip() for c in df.columns]

    stats = {
        "total_books": len(df),
        "avg_rating": round(df["My Rating"].mean(), 2) if "My Rating" in df else "N/A",
        "most_common_author": df["Author"].mode()[0] if "Author" in df else "N/A"
    }

    return render_template("dashboard.html", stat=stats)


# --------
# Run App
# --------

if __name__ == "__main__":
    app.run(debug=True)
