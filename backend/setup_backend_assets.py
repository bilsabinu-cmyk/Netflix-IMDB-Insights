import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "datasets"
MODEL_DIR = BASE_DIR / "models"

DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("Netflix + IMDb Dataset Builder")
print("=" * 60)
# ----------------------------------------
# Load Netflix Dataset
# ----------------------------------------

print("\nLoading Netflix dataset...")

netflix = pd.read_csv(DATA_DIR / "Netflix_movies_and_tv_shows_clustering.csv.zip")

print(f"Netflix Titles : {len(netflix)}")


# ----------------------------------------
# Load IMDb Dataset
# ----------------------------------------

print("\nLoading IMDb dataset...")

imdb = pd.read_csv(DATA_DIR / "imdb_top_1000.csv")

print(f"IMDb raw rows : {len(imdb)}")

# ----------------------------------------
# Clean Netflix Dataset
# ----------------------------------------

netflix = netflix.fillna("Unknown")

netflix["release_year"] = netflix["release_year"].astype(int)

netflix["description"] = netflix["description"].astype(str)


# ----------------------------------------
# Clean IMDb Dataset
# ----------------------------------------

# Ensure we have a text column to use as "review". The provided imdb_top_1000
# dataset uses "Overview" (or similar) instead of a "review" column.
if "review" in imdb.columns:
    imdb["review"] = imdb["review"].astype(str)
elif "Overview" in imdb.columns:
    imdb["review"] = imdb["Overview"].astype(str)
elif "overview" in imdb.columns:
    imdb["review"] = imdb["overview"].astype(str)
else:
    # Fallback: use first string-like column
    text_cols = imdb.select_dtypes(include=[object]).columns.tolist()
    if text_cols:
        imdb["review"] = imdb[text_cols[0]].astype(str)
    else:
        imdb["review"] = ""

# Create or normalize a sentiment label. If the file doesn't include a
# `sentiment` column, synthesize it from an available rating column (e.g.
# "IMDB_Rating"). Threshold of 7.0 -> positive.
if "sentiment" in imdb.columns:
    imdb["sentiment"] = imdb["sentiment"].astype(str).str.lower()
else:
    # Try to find a rating column
    rating_col = None
    for col in imdb.columns:
        if "rating" in col.lower():
            rating_col = col
            break
    if rating_col is not None:
        imdb[rating_col] = pd.to_numeric(imdb[rating_col], errors="coerce")
        # Use median split to ensure both classes exist for training
        med = imdb[rating_col].median()
        imdb["sentiment"] = imdb[rating_col].apply(lambda v: "positive" if pd.notna(v) and v >= med else "negative")
    else:
        # As last resort, mark all as positive so training can proceed.
        imdb["sentiment"] = "positive"

# Drop rows without review text
imdb = imdb.dropna(subset=["review"]).reset_index(drop=True)


print("\nDatasets Loaded Successfully.")
print("-" * 60)
# ----------------------------------------
# Train IMDb Sentiment Model
# ----------------------------------------

print("\nTraining IMDb Sentiment Model...")

X = imdb["review"]

y = imdb["sentiment"]

vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english"
)

X_vector = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_vector,
    y,
    test_size=0.2,
    random_state=42
)

logistic = LogisticRegression(max_iter=1000)

logistic.fit(X_train, y_train)

accuracy = logistic.score(X_test, y_test)

print(f"IMDb Sentiment Accuracy : {accuracy:.4f}")

joblib.dump(logistic, MODEL_DIR / "logistic.pkl")

joblib.dump(vectorizer, MODEL_DIR / "tfidf.pkl")

print("Sentiment model saved.")
# ----------------------------------------
# Prepare Netflix Dataset for Prediction
# ----------------------------------------

print("\nPreparing Netflix dataset...")

ml_df = netflix.copy()

encoder_type = LabelEncoder()
encoder_country = LabelEncoder()
encoder_rating = LabelEncoder()
encoder_genre = LabelEncoder()

ml_df["type"] = encoder_type.fit_transform(ml_df["type"])
ml_df["country"] = encoder_country.fit_transform(ml_df["country"])
ml_df["rating"] = encoder_rating.fit_transform(ml_df["rating"])
ml_df["listed_in"] = encoder_genre.fit_transform(ml_df["listed_in"])

joblib.dump(encoder_type, MODEL_DIR / "type_encoder.pkl")
joblib.dump(encoder_country, MODEL_DIR / "country_encoder.pkl")
joblib.dump(encoder_rating, MODEL_DIR / "rating_encoder.pkl")
joblib.dump(encoder_genre, MODEL_DIR / "genre_encoder.pkl")
joblib.dump(
    {
        "type": encoder_type,
        "country": encoder_country,
        "rating": encoder_rating,
        "listed_in": encoder_genre,
    },
    MODEL_DIR / "encoders.pkl"
)


# ----------------------------------------
# Create Target Variable
# ----------------------------------------

ml_df["target"] = np.where(
    ml_df["rating"] > ml_df["rating"].median(),
    1,
    0
)

X = ml_df[
    [
        "type",
        "country",
        "release_year",
        "rating",
        "listed_in"
    ]
]

y = ml_df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


# ----------------------------------------
# Decision Tree Model
# ----------------------------------------

decision_tree = DecisionTreeClassifier(
    random_state=42
)

decision_tree.fit(X_train, y_train)

joblib.dump(
    decision_tree,
    MODEL_DIR / "decision_tree.pkl"
)


# ----------------------------------------
# KNN Model
# ----------------------------------------

knn = KNeighborsClassifier(
    n_neighbors=5
)

knn.fit(X_train, y_train)

joblib.dump(
    knn,
    MODEL_DIR / "knn.pkl"
)

print("Decision Tree model saved.")
print("KNN model saved.")
# ----------------------------------------
# Predict Sentiment for Netflix Descriptions
# ----------------------------------------

print("\nPredicting sentiment for Netflix titles...")

description_vectors = vectorizer.transform(
    netflix["description"]
)

predicted_sentiment = logistic.predict(
    description_vectors
)

netflix["sentiment"] = predicted_sentiment


# ----------------------------------------
# Create Final Merged Dataset
# ----------------------------------------

merged_df = netflix[
    [
        "title",
        "type",
        "country",
        "release_year",
        "rating",
        "listed_in",
        "description",
        "sentiment"
    ]
].copy()

merged_df.to_csv(
    DATA_DIR / "merged_dataset.csv",
    index=False
)

print("\nMerged dataset created successfully!")

print(f"Total Records : {len(merged_df)}")

print("\nPreview:")
print(merged_df.head())

print("\nSaved to:")
print(DATA_DIR / "merged_dataset.csv")
# ----------------------------------------
# Model Evaluation
# ----------------------------------------

dt_accuracy = decision_tree.score(X_test, y_test)

knn_accuracy = knn.score(X_test, y_test)

print("\n" + "=" * 60)
print("TRAINING COMPLETED SUCCESSFULLY")
print("=" * 60)

print(f"Netflix Titles Loaded      : {len(netflix)}")
print(f"IMDb Reviews Loaded        : {len(imdb)}")
print(f"Merged Dataset Records     : {len(merged_df)}")

print("\nModel Accuracies")
print("-" * 30)
print(f"Logistic Regression : {accuracy:.4f}")
print(f"Decision Tree       : {dt_accuracy:.4f}")
print(f"KNN                 : {knn_accuracy:.4f}")

print("\nFiles Created")
print("-" * 30)
print(f"{DATA_DIR / 'merged_dataset.csv'}")
print(f"{MODEL_DIR / 'logistic.pkl'}")
print(f"{MODEL_DIR / 'tfidf.pkl'}")
print(f"{MODEL_DIR / 'decision_tree.pkl'}")
print(f"{MODEL_DIR / 'knn.pkl'}")
print(f"{MODEL_DIR / 'type_encoder.pkl'}")
print(f"{MODEL_DIR / 'country_encoder.pkl'}")
print(f"{MODEL_DIR / 'rating_encoder.pkl'}")
print(f"{MODEL_DIR / 'genre_encoder.pkl'}")

print("\nEverything is ready!")
print("Now run:")
print("python app.py")
print("=" * 60)