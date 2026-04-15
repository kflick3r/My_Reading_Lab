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
    df["Exclusive Shelf"] = df["Exclusive Shelf"].astype(str).str.strip().str.lower()

    read_df = df[df["Exclusive Shelf"] == "read"]
    to_read_df = df[df["Exclusive Shelf"] == "to-read"]
    current_df = df[df["Exclusive Shelf"] == "currently-reading"]
    
    # Insights on Data
    favorite_year = None
    best_year_count = None
    year_counts = pd.Series(dtype=int)

    if len(read_df) > 0:
        temp = read_df.copy()
        temp["Date Read"] = pd.to_datetime(temp["Date Read"], errors="coerce")
        temp = temp.dropna(subset=["Date Read"])

        temp["Year"] = temp["Date Read"].dt.year
        
        temp["Year"] = temp["Year"].astype("int64")

        year_counts = temp.groupby("Year").size().sort_index()

        if len(year_counts) > 0:
            favorite_year = int(year_counts.idxmax())
            best_year_count = int(year_counts.max())

    # ----- STATS -----
    stats = {
        "total_books": len(df),
        "books_read": len(read_df),
        "to_read": len(to_read_df),
        "currently_reading": len(current_df),
        "avg_rating": round(read_df["My Rating"].mean(), 2) if len(read_df) > 0 else "N/A",
        "most_common_author": read_df["Author"].mode()[0] if len(read_df) > 0 else "N/A",
        "favorite_year": favorite_year,
        "best_year_count": best_year_count
    }

    # Create Static folder if doesn't exsits
    os.makedirs("static", exist_ok=True)
    plt.style.use("seaborn-v0_8")

    # ----- CHART 1: Rating Distribution -----
    chart1_path = os.path.join("static", f"rating_{filename}.png")

    if len(read_df) > 0:
        plt.figure(figsize=(6, 4))

        rating_counts = read_df["My Rating"].value_counts().sort_index()
        rating_counts = rating_counts[rating_counts.index > 0]

        plt.bar(
            rating_counts.index.astype(int), 
            rating_counts.values,
            color="#F58518"
        )

        plt.title("Rating Distribution of Read Books")
        plt.xlabel("Rating")
        plt.ylabel("Count")
        plt.xticks([1, 2, 3, 4, 5])

        plt.tight_layout()
        plt.savefig(chart1_path, dpi=150)
        plt.close()

    # ----- CHART 2: Books Per Year -----
    chart2_path = os.path.join("static", f"year_{filename}.png")

    if len(year_counts) > 0:
        plt.figure(figsize=(7,4))

        plt.bar(
            year_counts.index.astype(int), 
            year_counts.values, 
            color="#4C78A8"
        )

        plt.title("Books Read Per Year")
        plt.xlabel("Year")
        plt.ylabel("Books")
        
        plt.xticks(year_counts.index.astype(int))
        plt.grid(axis="y", linestyle="--", alpha=0.3)

        plt.tight_layout()
        plt.savefig(chart2_path, dpi=150)
        plt.close()

    # Render
    return render_template(
        "dashboard.html", 
        stats=stats,
        chart1=f"rating_{filename}.png",
        chart2=f"year_{filename}.png"
        )


# --------
# Run App
# --------

if __name__ == "__main__":
    app.run(debug=True)
