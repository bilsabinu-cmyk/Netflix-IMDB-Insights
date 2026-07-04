from flask import Flask, jsonify, request
from flask_cors import CORS

import pandas as pd
import joblib

app = Flask(__name__)
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

# ------------------------------------------
# Load Dataset
# ------------------------------------------

df = pd.read_csv("datasets/merged_dataset.csv")

# ------------------------------------------
# Load Models
# ------------------------------------------

decision_tree = joblib.load("models/decision_tree.pkl")
logistic = joblib.load("models/logistic.pkl")
knn = joblib.load("models/knn.pkl")
encoders = joblib.load("models/encoders.pkl")

# ------------------------------------------
# HOME
# ------------------------------------------

@app.route("/")
def home():

    return jsonify({

        "Project":"Netflix & IMDb Insights",

        "Version":"1.0",

        "Status":"Running"

    })

# ------------------------------------------
# DASHBOARD
# ------------------------------------------

@app.route("/dashboard", methods=["GET"])
def dashboard():

    total_titles = len(df)

    movies = len(df[df["type"]=="Movie"])

    tvshows = len(df[df["type"]=="TV Show"])

    positive = len(df[df["sentiment"]=="positive"])

    negative = len(df[df["sentiment"]=="negative"])

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

        "Total Titles":total_titles,

        "Movies":movies,

        "TV Shows":tvshows,

        "Positive Reviews":positive,

        "Negative Reviews":negative,

        "Top Genres":top_genres,

        "Top Countries":top_countries

    })

# ------------------------------------------
# SEARCH MOVIE
# ------------------------------------------

@app.route("/search/<title>", methods=["GET"])
def search(title):

    result = df[

        df["title"]

        .str.lower()

        .str.contains(title.lower())

    ]

    if len(result)==0:

        return jsonify({

            "message":"Movie Not Found"

        })

    return jsonify(

        result.to_dict(

            orient="records"

        )

    )

# ------------------------------------------
# TOP MOVIES
# ------------------------------------------

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

    return jsonify(

        data.head(20).to_dict(

            orient="records"

        )

    )

# ------------------------------------------
# PREDICT
# ------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    data = request.json

    type_value = transform_encoder(encoders["type"], data.get("type"), "type")

    country_value = transform_encoder(encoders["country"], data.get("country"), "country")

    rating_value = transform_encoder(encoders["rating"], data.get("rating"), "rating")

    genre_value = transform_encoder(encoders["listed_in"], data.get("listed_in"), "listed_in")

    year = int(data.get("release_year"))

    sample = [[

        type_value,

        country_value,

        year,

        rating_value,

        genre_value

    ]]

    prediction = decision_tree.predict(sample)[0]

    if prediction==1:

        result="High Rated"

    else:

        result="Low Rated"

    return jsonify({

        "Prediction":result,

        "Model":"Decision Tree"

    })

# ------------------------------------------
# GENRES
# ------------------------------------------

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

# ------------------------------------------
# COUNTRIES
# ------------------------------------------

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

# ------------------------------------------
# YEAR ANALYSIS
# ------------------------------------------

@app.route("/years", methods=["GET"])
def years():

    years = (

        df["release_year"]

        .value_counts()

        .sort_index()

        .to_dict()

    )

    return jsonify(years)

# ------------------------------------------
# SENTIMENT
# ------------------------------------------

@app.route("/sentiment", methods=["GET"])
def sentiment():

    sentiment = (

        df["sentiment"]

        .value_counts()

        .to_dict()

    )

    return jsonify(sentiment)

# ------------------------------------------
# RUN
# ------------------------------------------

if __name__=="__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )