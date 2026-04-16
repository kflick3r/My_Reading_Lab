from flask import Flask, render_template, request, redirect, url_for
import plotly.graph_objects as go
import plotly.io as pio
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

    theme = request.form.get("theme", "light")

    return redirect(url_for("analyze", filename=filename, theme=theme))

# Analysis Page
@app.route("/analyze/<filename>")
def analyze(filename):
    theme = request.args.get("theme", "light")
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

    plotly_template = "plotly_dark" if theme == "dark" else "simple_white"
    # ----- CHART 1: Rating Distribution -----
    if len(read_df) > 0:
        rating_counts = read_df["My Rating"].value_counts().sort_index()
        rating_counts = rating_counts[rating_counts.index > 0]

        ratings = rating_counts.index.astype(int)
        values = rating_counts.values

        color_map = {
            1: "#F3C2C2",
            2: "#D48585",
            3: "#B63838", 
            4: "#860B0B",
            5: "#580000",
        }

        colors = [color_map.get(r, "#999999") for r in ratings]

        fig1 = go.Figure(
            data=[
                go.Bar(
                    x=ratings,
                    y=values,
                    marker_color=colors
                )
            ]
        )

        fig1.update_traces(marker_line_color='black', marker_line_width=1)

        fig1.update_layout(
            title="Rating Distribution of Read Books",
            xaxis_title="Rating",
            yaxis_title="Count",
            template=plotly_template,
        
            xaxis=dict(
                range=[0.5, 5.5],   # locks visual range
            dtick=1,            # only show whole numbers
            fixedrange=True     # disables zoom/pan on x-axis
            ),
    
            yaxis=dict(
                rangemode="tozero", # always start at 0
                fixedrange=True     # disables zoom/pan on y-axis
            ),
            autosize=True
        )
    else:
        fig1 = go.Figure()
        fig1.update_layout(title="No rating data available")

    chart1_html = pio.to_html(fig1, full_html=False, config={"responsive": True})


    # ----- CHART 2: Books Per Year -----
    if len(year_counts) > 0:
        fig2 = go.Figure(
            data=[
                go.Bar(
                    x=year_counts.index,
                    y=year_counts.values,
                    marker_color="#4B6886"
                )
            ]
        )

        fig2.update_traces(marker_line_color='black', marker_line_width=1)

        fig2.update_layout(
            title="Books Read Per Year",
            xaxis_title="Year",
            yaxis_title="Books",
            template=plotly_template,

            yaxis=dict(fixedrange=True),
            xaxis=dict(fixedrange=True),
            autosize=True
        )
    else:
        fig2 = go.Figure()
        fig2.update_layout(title="No year data available")

    chart2_html = pio.to_html(fig2, full_html=False, config={"responsive": True}) 

    # Render
    return render_template(
        "dashboard.html", 
        stats=stats,
        chart1=chart1_html,
        chart2=chart2_html
    )


# --------
# Run App
# --------

if __name__ == "__main__":
    app.run(debug=True)
