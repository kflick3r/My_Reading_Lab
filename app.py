from flask import Flask, render_template, request, redirect, url_for
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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

    # Import time to save with filename to advoid collision
    import time
    filename = str(int(time.time())) + "_" + file.filename

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    return redirect(url_for("analyze", filename=filename))

# Analysis Page
@app.route("/analyze/<filename>")
def analyze(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    

    df = pd.read_csv(file_path)
    # Clean Up Goodreads CSV
    df.columns = [c.strip() for c in df.columns]

    # Split up based on reading status 
    read_df = df[df["Exclusive Shelf"] == "read"]
    to_read_df = df[df["Exclusive Shelf"] == "to-read"]
    current_df = df[df["Exclusive Shelf"] == "currently-reading"]
    
    # ----- STATS -----
    stats = {
        "total_books": len(df),
        "books_read": len(read_df),
        "to_read": len(to_read_df),
        "currently_reading": len(current_df),
        "avg_rating": round(read_df["My Rating"].mean(), 2) if len(read_df) > 0 else "N/A",
        "most_common_author": read_df["Author"].mode()[0] if len(read_df) > 0 else "N/A"
    }

    # Create Static folder if doesn't exsits
    os.makedirs("static", exist_ok=True)

    # ----- CHART 1: Rating Distribution -----
    chart1_path = os.path.join("static", "rating_chart.png")

    if len(read_df) > 0:
        plt.figure()
        read_df["My Rating"].value_counts().sort_index().plot(kind="bar")
        plt.title("Rating Distribution of Read Books")
        plt.xlabel("Rating")
        plt.ylabel("Count")
        plt.savefig(chart1_path)
        plt.close()

    # ----- CHART 2: Books Per Year -----
    chart2_path = os.path.join("static", "year_chart.png")

    if len(read_df) > 0:
        temp = read_df.copy()
        temp["Date Read"] = pd.to_datetime(temp["Date Read"], errors="coerce")
        temp["Year"] = temp["Date Read"].dt.year

        plt.figure()
        temp["Year"].value_counts().sort_index().plot(kind="line", marker="o")
        plt.title("Books Read Per Year")
        plt.xlabel("Year")
        plt.ylabel("Books")
        plt.savefig(chart2_path)
        plt.close()

    return render_template(
        "dashboard.html", 
        stats=stats,
        chart1="rating_chart.png",
        chart2="year_chart.png"
        )


# --------
# Run App
# --------

if __name__ == "__main__":
    app.run(debug=True)
