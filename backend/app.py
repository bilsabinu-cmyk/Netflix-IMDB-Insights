from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import joblib

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datasets"
MODEL_DIR = BASE_DIR / "models"

app = Flask(__name__,static_folder="../frontend/build", static_url_path="/")
CORS(app)


def transform_encoder(encoder, value, field):
    if value is None:
        raise ValueError(f"Missing value for {field}")
    value_str = str(value).strip()
    if value_str == "":
        raise ValueError(f"Missing value for {field}")
    classes = [str(c) for c in encoder.classes_]
    match = next((c for c in classes if c.lower() == value_str.lower()), None)
    if match is None:
        raise ValueError(
            f"Invalid {field} '{value_str}'. Valid values include: {', '.join(classes[:10])}"
        )
    return encoder.transform([match])[0]


def load_dataset():
    dataset_path = DATA_DIR / "merged_dataset.csv"
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found. Create {dataset_path} or run backend/setup_backend_assets.py"
        )
    return pd.read_csv(dataset_path)


def load_model(filename):
    path = MODEL_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Model file not found: {path}. Create it with backend/setup_backend_assets.py"
        )
    return joblib.load(path)


df = load_dataset()

decision_tree = load_model("decision_tree.pkl")
logistic = load_model("logistic.pkl")
knn = load_model("knn.pkl")
encoders = load_model("encoders.pkl")


@app.route("/")
def home():
    return send_from_directory("../frontend/build", "index.html")


@app.route("/css/<path:filename>")
def css_files(filename):
    return send_from_directory("../frontend/css", filename)


@app.route("/js/<path:filename>")
def js_files(filename):
    return send_from_directory("../frontend/js", filename)

@app.route("/dashboard", methods=["GET"])
def dashboard():
    total_titles = len(df)
    movies = len(df[df["type"] == "Movie"])
    tvshows = len(df[df["type"] == "TV Show"])
    positive = len(df[df["sentiment"] == "positive"])
    negative = len(df[df["sentiment"] == "negative"])
    top_genres = (
        df["listed_in"]
        .str.split(", ")
        .explode()
        .value_counts()
        .head(10)
        .to_dict()
    )
    top_countries = (
        df["country"]
        .str.split(", ")
        .explode()
        .value_counts()
        .head(10)
        .to_dict()
    )
    return jsonify({
        "Total Titles": total_titles,
        "Movies": movies,
        "TV Shows": tvshows,
        "Positive Reviews": positive,
        "Negative Reviews": negative,
        "Top Genres": top_genres,
        "Top Countries": top_countries
    })


@app.route("/search/<title>", methods=["GET"])
def search(title):
    result = df[
        df["title"]
        .str.lower()
        .str.contains(title.lower())
    ]
    if len(result) == 0:
        return jsonify({"message": "Movie Not Found"}), 404
    return jsonify(result.to_dict(orient="records"))


@app.route("/topmovies", methods=["GET"])
def top_movies():
    data = df[
        [
            "title",
            "type",
            "country",
            "listed_in",
            "release_year",
            "sentiment"
        ]
    ]
    return jsonify(data.head(20).to_dict(orient="records"))


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    try:
        type_value = transform_encoder(encoders["type"], data.get("type"), "type")
        country_value = transform_encoder(encoders["country"], data.get("country"), "country")
        rating_value = transform_encoder(encoders["rating"], data.get("rating"), "rating")
        genre_value = transform_encoder(encoders["listed_in"], data.get("listed_in"), "listed_in")
        year = int(data.get("release_year"))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    sample = [[type_value, country_value, year, rating_value, genre_value]]
    prediction = decision_tree.predict(sample)[0]
    result = "High Rated" if prediction == 1 else "Low Rated"
    return jsonify({"Prediction": result, "Model": "Decision Tree"})


@app.route("/genres", methods=["GET"])
def genres():
    genre = (
        df["listed_in"]
        .str.split(", ")
        .explode()
        .value_counts()
        .to_dict()
    )
    return jsonify(genre)


@app.route("/countries", methods=["GET"])
def countries():
    country = (
        df["country"]
        .str.split(", ")
        .explode()
        .value_counts()
        .to_dict()
    )
    return jsonify(country)


@app.route("/years", methods=["GET"])
def years():
    years = (
        df["release_year"]
        .value_counts()
        .sort_index()
        .to_dict()
    )
    return jsonify(years)


@app.route("/sentiment", methods=["GET"])
def sentiment():
    sentiment = df["sentiment"].value_counts().to_dict()
    return jsonify(sentiment)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "Running",
        "backend": "Flask",
        "model": "Decision Tree",
        "version": "1.0"
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
