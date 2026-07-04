import pandas as pd

# -----------------------------
# Load Dataset
# -----------------------------

df = pd.read_csv("datasets/merged_dataset.csv")

# -----------------------------
# Dashboard Summary
# -----------------------------

def dashboard_summary():

    return {

        "total_titles": len(df),

        "movies": len(df[df["type"] == "Movie"]),

        "tv_shows": len(df[df["type"] == "TV Show"]),

        "countries": df["country"].nunique(),

        "genres": df["listed_in"].nunique()

    }

# -----------------------------
# Top Genres
# -----------------------------

def top_genres():

    return (

        df["listed_in"]

        .str.split(", ")

        .explode()

        .value_counts()

        .head(10)

        .to_dict()

    )

# -----------------------------
# Top Countries
# -----------------------------

def top_countries():

    return (

        df["country"]

        .str.split(", ")

        .explode()

        .value_counts()

        .head(10)

        .to_dict()

    )

# -----------------------------
# Year Analysis
# -----------------------------

def year_analysis():

    return (

        df["release_year"]

        .value_counts()

        .sort_index()

        .to_dict()

    )

# -----------------------------
# Sentiment
# -----------------------------

def sentiment_analysis():

    return df["sentiment"].value_counts().to_dict()

# -----------------------------
# Search Movie
# -----------------------------

def search_movie(title):

    result = df[

        df["title"]

        .str.lower()

        .str.contains(title.lower())

    ]

    return result.to_dict(orient="records")

# -----------------------------
# Top Movies
# -----------------------------

def top_movies():

    positive = df[

        df["sentiment"] == "positive"

    ]

    positive = positive.sort_values(

        by="release_year",

        ascending=False

    )

    return positive.head(20).to_dict(

        orient="records"

    )

# -----------------------------
# Genre Count
# -----------------------------

def genre_count():

    genre = (

        df["listed_in"]

        .str.split(", ")

        .explode()

        .value_counts()

    )

    return genre.to_dict()

# -----------------------------
# Country Count
# -----------------------------

def country_count():

    country = (

        df["country"]

        .str.split(", ")

        .explode()

        .value_counts()

    )

    return country.to_dict()

# -----------------------------
# Latest Releases
# -----------------------------

def latest_movies():

    latest = df.sort_values(

        by="release_year",

        ascending=False

    )

    return latest.head(20).to_dict(

        orient="records"

    )

# -----------------------------
# Movies Only
# -----------------------------

def movies():

    movie = df[

        df["type"] == "Movie"

    ]

    return movie.to_dict(

        orient="records"

    )

# -----------------------------
# TV Shows Only
# -----------------------------

def tvshows():

    show = df[

        df["type"] == "TV Show"

    ]

    return show.to_dict(

        orient="records"

    )