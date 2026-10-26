#!/usr/bin/env python
# coding: utf-8

# %% [markdown]
# Cell 0
# # StreamHaven: Analyzing Streaming Fragmentation
#
# ![Banner](./assets/banner.jpeg)
#
# This notebook imports, combines, explores, cleans, and visualizes movie ratings and U.S. streaming-provider data for the StreamHaven project.

# %% [markdown]
# Cell 1
# ## Topic
#
# Streaming content is divided across many platforms. Viewers may have difficulty finding a movie or may need several subscriptions to access the movies they want. This fragmentation can make streaming confusing, inconvenient, and expensive.
#
# This project analyzes the availability of popular and highly rated movies across U.S. subscription streaming services. The results can guide the continued development of **StreamHaven**, a centralized platform where users can search for movies and see where they are available.
#
# The project focuses on approximately 300 movies with substantial IMDb voting activity. Restricting the analysis to movies, the United States, and subscription availability keeps the scope manageable and measurable.

# %% [markdown]
# Cell 2
# ## Project Questions
#
# 1. Which streaming providers offer the largest number of selected movies?
# 2. How many subscription services typically offer each selected movie?
# 3. What percentage of the movies are exclusive, available from multiple services, or unavailable by subscription?
# 4. Which genres are the most and least available across subscription platforms?
# 5. Is there a relationship between a movie's rating, popularity, and number of available providers?
# 6. Which selected movies are unavailable through the subscription services represented in the data?

# %% [markdown]
# Cell 3
# ## What Would an Answer Look Like?
#
# An answer will include provider-coverage totals, the distribution of provider counts per movie, genre availability, and the relationship between ratings or popularity and provider availability. Charts and summary tables will identify the providers with the strongest coverage and show how fragmented the selected catalog is.
#
# An example conclusion could state that one provider carries the largest percentage of selected movies, but viewers would still need multiple subscriptions to access most highly rated titles.

# %% [markdown]
# Cell 4
# ## Data Sources
#
# ### 1. MovieLens Latest Small — File source
#
# MovieLens supplies `movies.csv`, `ratings.csv`, and `links.csv`. These files provide movie titles, genres, user ratings, and identifiers connecting movies to IMDb and TMDB.
#
# Source: [MovieLens Latest Datasets](https://grouplens.org/datasets/movielens/latest/)
#
# ### 2. IMDb Non-Commercial Dataset — File source
#
# IMDb supplies average ratings and vote counts. Vote counts are used to select movies with enough audience activity for meaningful comparisons.
#
# Source: [IMDb Title Ratings Dataset](https://datasets.imdbws.com/title.ratings.tsv.gz)
#
# ### 3. TMDB Watch Providers — API source
#
# The TMDB API supplies U.S. watch-provider availability. This analysis uses the `flatrate` category to represent subscription streaming.
#
# Source: [TMDB Movie Watch Providers API](https://developer.themoviedb.org/reference/movie-watch-providers)
#
# ### How the Sources Relate
#
# MovieLens acts as the bridge. Its `movieId` connects the MovieLens files, `imdbId` connects to IMDb's `tconst`, and `tmdbId` is used to request provider information from TMDB.

# %% [markdown]
# Cell 5
# ## Approach and Analysis
#
# The analysis imports the three sources, aggregates MovieLens user ratings, selects approximately 300 popular movies, and requests U.S. provider availability from TMDB. It then creates one cleaned movie-level dataset containing ratings, vote counts, genres, release years, and subscription-provider counts.
#
# The exploratory analysis examines distributions, correlations, missing values, duplicates, data types, and outliers. Four visualizations use Matplotlib and Seaborn to compare provider coverage, fragmentation, genre availability, and the relationship between popularity and availability.

# %% [markdown]
# Cell 6
# ## Setup and Data Import

# %%
# Cell 7
from getpass import getpass
from io import BytesIO
import os
from pathlib import Path
import time
from zipfile import ZipFile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns

pd.set_option("display.max_columns", 50)
sns.set_theme(style="whitegrid")

data_folder = Path("data")
data_folder.mkdir(exist_ok=True)

print("Setup complete")

# %% [markdown]
# Cell 8
# ### Import MovieLens files

# %%
# Cell 9
movielens_url = (
    "https://files.grouplens.org/datasets/"
    "movielens/ml-latest-small.zip"
)

response = requests.get(movielens_url, timeout=60)
response.raise_for_status()

with ZipFile(BytesIO(response.content)) as zip_file:
    zip_file.extractall(data_folder)

movielens_folder = data_folder / "ml-latest-small"
movies = pd.read_csv(movielens_folder / "movies.csv")
ratings = pd.read_csv(movielens_folder / "ratings.csv")
links = pd.read_csv(movielens_folder / "links.csv")

print("Movies:", movies.shape)
print("Ratings:", ratings.shape)
print("Links:", links.shape)
movies.head()

# %% [markdown]
# Cell 10
# ### Prepare MovieLens identifiers and rating summaries

# %%
# Cell 11
links["tconst"] = (
    "tt" + links["imdbId"].astype("Int64").astype(str).str.zfill(7)
)

movielens_summary = (
    ratings.groupby("movieId")["rating"]
    .agg(movielens_rating="mean", movielens_rating_count="count")
    .reset_index()
)

movielens_data = (
    movies.merge(links, on="movieId", how="left")
    .merge(movielens_summary, on="movieId", how="left")
)

movielens_data.head()

# %% [markdown]
# Cell 12
# ### Import IMDb ratings and combine the file sources

# %%
# Cell 13
imdb_url = "https://datasets.imdbws.com/title.ratings.tsv.gz"

imdb_ratings = pd.read_csv(
    imdb_url,
    sep="	",
    compression="gzip",
    na_values="\\N"
)

movie_data = movielens_data.merge(
    imdb_ratings,
    on="tconst",
    how="left"
)

print("IMDb ratings:", imdb_ratings.shape)
print("Combined file data:", movie_data.shape)
movie_data.head()

# %% [markdown]
# Cell 14
# ### Select the project movie sample

# %%
# Cell 15
project_movies = (
    movie_data
    .dropna(subset=["tmdbId", "averageRating", "numVotes"])
    .query("numVotes >= 25000")
    .sort_values(["numVotes", "averageRating"], ascending=False)
    .head(300)
    .copy()
)

project_movies["tmdbId"] = project_movies["tmdbId"].astype(int)
project_movies["release_year"] = pd.to_numeric(
    project_movies["title"].str.extract(r"\((\d{4})\)\s*$")[0],
    errors="coerce"
).astype("Int64")

print("Selected movies:", project_movies.shape)
project_movies.head()

# %% [markdown]
# Cell 16
# ### Import TMDB watch-provider data
#
# The API key is entered through a hidden prompt and is never stored in this notebook. Use the shorter credential labeled **API Key** on the TMDB API settings page. An environment variable named `TMDB_API_KEY` can also be used.

# %%
# Cell 17
tmdb_api_key = os.getenv("TMDB_API_KEY")

if not tmdb_api_key:
    tmdb_api_key = getpass("Paste your TMDB API Key: ").strip()

test_response = requests.get(
    "https://api.themoviedb.org/3/movie/550/watch/providers",
    params={"api_key": tmdb_api_key},
    timeout=30
)

if test_response.status_code != 200:
    message = test_response.json().get("status_message", "Unknown TMDB error")
    raise RuntimeError(
        f"TMDB authentication failed ({test_response.status_code}): {message}"
    )

print("TMDB connection successful")

# %%
# Cell 18
provider_records = []
missing_movies = []
failed_requests = []

for tmdb_id in project_movies["tmdbId"]:
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/watch/providers"
    response = requests.get(
        url,
        params={"api_key": tmdb_api_key},
        timeout=30
    )

    if response.status_code == 404:
        missing_movies.append(tmdb_id)
        continue

    if response.status_code != 200:
        failed_requests.append((tmdb_id, response.status_code))
        continue

    us_results = response.json().get("results", {}).get("US", {})

    for access_type in ["flatrate", "free", "ads", "rent", "buy"]:
        for provider in us_results.get(access_type, []):
            provider_records.append({
                "tmdbId": tmdb_id,
                "provider_id": provider["provider_id"],
                "provider_name": provider["provider_name"],
                "access_type": access_type,
                "country": "US"
            })

    time.sleep(0.03)

watch_providers = pd.DataFrame(
    provider_records,
    columns=[
        "tmdbId",
        "provider_id",
        "provider_name",
        "access_type",
        "country"
    ]
)

print("TMDB provider records:", watch_providers.shape)
print("Missing movie IDs:", len(missing_movies))
print("Other failed requests:", failed_requests[:10])
watch_providers.head()

# %% [markdown]
# Cell 19
# ### Combine all three sources

# %%
# Cell 20
subscription_providers = (
    watch_providers.loc[watch_providers["access_type"] == "flatrate"]
    .drop_duplicates(subset=["tmdbId", "provider_id"])
    .copy()
)

analysis_data = project_movies.merge(
    subscription_providers,
    on="tmdbId",
    how="left"
)

print("Subscription-provider records:", subscription_providers.shape)
print("Combined analysis records:", analysis_data.shape)
analysis_data.head()

# %% [markdown]
# Cell 21
# ## Exploratory Data Analysis
#
# The initial EDA checks the size and structure of each source, summarizes numerical variables, and identifies missing values, duplicates, data-type issues, and possible outliers. Provider-level data naturally repeats a movie when it is available on more than one service, so duplicate checks use the appropriate identifiers rather than treating every repeated movie as an error.

# %%
# Cell 22
print("Project movies:", project_movies.shape)
print("Watch-provider records:", watch_providers.shape)
print("Combined analysis records:", analysis_data.shape)

analysis_data.info()

# %%
# Cell 23
summary_columns = [
    "movielens_rating",
    "movielens_rating_count",
    "averageRating",
    "numVotes",
    "release_year"
]

analysis_data[summary_columns].describe().T

# %%
# Cell 24
missing_summary = (
    analysis_data.isna().sum()
    .to_frame("missing_count")
    .assign(missing_percent=lambda frame: frame["missing_count"] / len(analysis_data) * 100)
    .sort_values("missing_count", ascending=False)
)

duplicate_movies = project_movies.duplicated(subset="movieId").sum()
duplicate_provider_pairs = subscription_providers.duplicated(
    subset=["tmdbId", "provider_id"]
).sum()

print("Duplicate movies:", duplicate_movies)
print("Duplicate movie-provider pairs:", duplicate_provider_pairs)
missing_summary.head(12)

# %% [markdown]
# Cell 25
# ### Initial Data Issues
#
# - Missing provider values represent movies with no U.S. subscription result, not automatically bad records.
# - `tmdbId` and `release_year` should be integer-like values.
# - A movie-provider pair should appear only once in the subscription data.
# - Extremely large IMDb vote counts may appear as outliers. They represent genuinely popular movies, so they are retained and a logarithmic scale is used where appropriate.
# - Movie genres contain multiple values separated by `|`; they must be split before genre-level analysis.

# %%
# Cell 26
q1 = project_movies["numVotes"].quantile(0.25)
q3 = project_movies["numVotes"].quantile(0.75)
iqr = q3 - q1
vote_outlier_threshold = q3 + 1.5 * iqr

vote_outliers = project_movies.loc[
    project_movies["numVotes"] > vote_outlier_threshold,
    ["title", "numVotes", "averageRating"]
].sort_values("numVotes", ascending=False)

print("Vote-count outlier threshold:", round(vote_outlier_threshold))
print("Number of high-vote outliers:", len(vote_outliers))
vote_outliers.head(10)

# %% [markdown]
# Cell 27
# ## Data Cleaning and Transformation
#
# The cleaning process preserves the raw imported DataFrames and creates new cleaned versions. Duplicate movie and movie-provider records are removed, identifier and year fields are converted to appropriate types, and provider counts are calculated at the movie level. Movies without a subscription provider are assigned a provider count of zero. Genres are split into individual categories for comparison. Valid popularity outliers are retained because removing famous movies would weaken the project's focus on popular titles.

# %%
# Cell 28
clean_movies = (
    project_movies
    .drop_duplicates(subset="movieId")
    .copy()
)

clean_movies["tmdbId"] = pd.to_numeric(
    clean_movies["tmdbId"], errors="coerce"
).astype("Int64")
clean_movies["release_year"] = pd.to_numeric(
    clean_movies["release_year"], errors="coerce"
).astype("Int64")

clean_providers = (
    subscription_providers
    .dropna(subset=["tmdbId", "provider_id", "provider_name"])
    .drop_duplicates(subset=["tmdbId", "provider_id"])
    .copy()
)

provider_counts = (
    clean_providers.groupby("tmdbId")["provider_id"]
    .nunique()
    .rename("provider_count")
    .reset_index()
)

movie_level_data = clean_movies.merge(
    provider_counts,
    on="tmdbId",
    how="left"
)
movie_level_data["provider_count"] = (
    movie_level_data["provider_count"].fillna(0).astype(int)
)

genre_data = movie_level_data.assign(
    genre=movie_level_data["genres"].str.split("|")
).explode("genre")
genre_data = genre_data.loc[genre_data["genre"] != "(no genres listed)"].copy()

print("Clean movie-level data:", movie_level_data.shape)
print("Missing values after cleaning:")
print(movie_level_data.isna().sum().loc[lambda values: values > 0])
movie_level_data.head()

# %% [markdown]
# Cell 29
# The remaining missing release years, if any, are left as missing because guessing a year could introduce false information. The important analytical fields—ratings, vote counts, IDs, and provider counts—are complete in the movie-level dataset.

# %%
# Cell 30
numeric_columns = [
    "movielens_rating",
    "movielens_rating_count",
    "averageRating",
    "numVotes",
    "release_year",
    "provider_count"
]

correlation_matrix = movie_level_data[numeric_columns].corr()
correlation_matrix.round(2)

# %% [markdown]
# Cell 31
# The correlation matrix measures linear relationships among the numerical variables. A value near 1 or -1 indicates a stronger relationship, while a value near 0 indicates little linear relationship. Correlation does not prove that one variable causes another.

# %% [markdown]
# Cell 32
# ## Data Visualizations

# %% [markdown]
# Cell 33
# ### Visualization 1: Movies Available by Provider
#
# This Seaborn bar chart compares provider coverage. A taller bar means that the provider offers more movies from the selected popular-movie sample.

# %%
# Cell 34
provider_coverage = (
    clean_providers.groupby("provider_name")["tmdbId"]
    .nunique()
    .sort_values(ascending=False)
    .head(15)
    .reset_index(name="movie_count")
)

plt.figure(figsize=(11, 6))
sns.barplot(
    data=provider_coverage,
    x="movie_count",
    y="provider_name",
    color="#3366cc"
)
plt.title("Top U.S. Subscription Providers by Selected Movie Coverage")
plt.xlabel("Number of selected movies")
plt.ylabel("Streaming provider")
plt.tight_layout()
plt.show()

# %% [markdown]
# Cell 35
# **Insight:** The chart identifies which providers have the broadest coverage of the selected catalog. Even the leading provider may cover only part of the catalog, which demonstrates fragmentation.

# %% [markdown]
# Cell 36
# ### Visualization 2: Number of Providers per Movie
#
# This Matplotlib histogram shows how widely each movie is distributed. Values of zero represent movies without a U.S. subscription result, one represents an exclusive title in this dataset, and larger values represent broader availability.

# %%
# Cell 37
max_provider_count = int(movie_level_data["provider_count"].max())
bins = np.arange(-0.5, max_provider_count + 1.5, 1)

plt.figure(figsize=(9, 5))
plt.hist(
    movie_level_data["provider_count"],
    bins=bins,
    color="#ff8c42",
    edgecolor="black"
)
plt.title("Distribution of Subscription Providers per Movie")
plt.xlabel("Number of providers")
plt.ylabel("Number of movies")
plt.xticks(range(max_provider_count + 1))
plt.tight_layout()
plt.show()

# %% [markdown]
# Cell 38
# **Insight:** Concentration around zero or one provider indicates limited availability or exclusivity. A wider distribution indicates that some titles are easier to access across competing services.

# %% [markdown]
# Cell 39
# ### Visualization 3: Average Availability by Genre
#
# This Seaborn chart compares the average number of providers per movie for the most common genres. Using an average makes genres with different numbers of movies easier to compare.

# %%
# Cell 40
top_genres = genre_data["genre"].value_counts().head(12).index
genre_availability = (
    genre_data.loc[genre_data["genre"].isin(top_genres)]
    .groupby("genre")
    .agg(
        average_provider_count=("provider_count", "mean"),
        movie_count=("movieId", "nunique")
    )
    .sort_values("average_provider_count", ascending=False)
    .reset_index()
)

plt.figure(figsize=(10, 6))
sns.barplot(
    data=genre_availability,
    x="average_provider_count",
    y="genre",
    color="#2a9d8f"
)
plt.title("Average Subscription Availability by Genre")
plt.xlabel("Average number of providers per movie")
plt.ylabel("Genre")
plt.tight_layout()
plt.show()

# %% [markdown]
# Cell 41
# **Insight:** Differences among genres show whether some types of movies are easier to find than others. The `movie_count` column should also be considered because averages based on fewer movies may be less stable.

# %% [markdown]
# Cell 42
# ### Visualization 4: Popularity and Provider Availability
#
# This Seaborn scatter plot compares IMDb vote count with provider count. The logarithmic x-axis prevents extremely popular movies from compressing the rest of the chart. Color represents IMDb rating.

# %%
# Cell 43
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=movie_level_data,
    x="numVotes",
    y="provider_count",
    hue="averageRating",
    palette="viridis",
    alpha=0.75
)
plt.xscale("log")
plt.title("IMDb Popularity Compared with Subscription Availability")
plt.xlabel("IMDb votes (log scale)")
plt.ylabel("Number of providers")
plt.legend(title="IMDb rating", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.show()

# %% [markdown]
# Cell 44
# **Insight:** The plot shows whether highly rated or heavily voted movies tend to appear on more services. A scattered pattern would suggest that popularity alone does not determine subscription availability.

# %% [markdown]
# Cell 45
# ### Additional Fragmentation Summary

# %%
# Cell 46
fragmentation_summary = pd.Series({
    "Unavailable by subscription": (movie_level_data["provider_count"] == 0).sum(),
    "Available from one provider": (movie_level_data["provider_count"] == 1).sum(),
    "Available from multiple providers": (movie_level_data["provider_count"] > 1).sum()
}).to_frame("movie_count")

fragmentation_summary["percent"] = (
    fragmentation_summary["movie_count"] / len(movie_level_data) * 100
).round(1)

fragmentation_summary

# %% [markdown]
# Cell 47
# This table directly summarizes fragmentation. Titles with zero providers are unavailable through the subscription services returned by TMDB, titles with one provider are exclusive within this dataset, and titles with multiple providers offer viewers more flexibility.

# %% [markdown]
# Cell 48
# ## Machine Learning Plan
#
# I plan to use **supervised regression** to predict the number of subscription providers offering a movie. The target variable will be `provider_count`. Potential features include IMDb rating, IMDb vote count, MovieLens rating, MovieLens rating count, release year, and encoded genres.
#
# The main challenges are the limited sample size, missing provider information, multi-value genre data, highly skewed vote counts, and the possibility that many movies have zero or one provider. I will address these issues by using the cleaned movie-level dataset, one-hot encoding genres, applying a logarithmic transformation to vote counts, and separating the data into training and testing sets. I will compare training and testing performance to detect overfitting or underfitting. Because provider count is discrete and may be concentrated near zero, I may also compare standard regression with a count-based model.

# %% [markdown]
# Cell 49
# ## Prior Feedback and Updates
#
# Feedback on the original project helped narrow the scope. The first idea included streaming prices, user behavior, content removal, and availability. The updated project focuses on a question that can be measured with the available sources: how fragmented are popular movies across U.S. subscription streaming services?
#
# The project now uses a defined movie sample, limits availability to the United States and subscription services, uses MovieLens identifiers to connect all sources, and documents TMDB records that are missing or fail instead of allowing one request to stop the full import.

# %% [markdown]
# Cell 50
# ## Save the Prepared Data

# %%
# Cell 51
project_movies.to_csv(data_folder / "project_movies.csv", index=False)
watch_providers.to_csv(data_folder / "watch_providers.csv", index=False)
analysis_data.to_csv(data_folder / "streamhaven_analysis_data.csv", index=False)
movie_level_data.to_csv(data_folder / "streamhaven_movie_level.csv", index=False)

print("Prepared data files saved in the data folder")

# %% [markdown]
# Cell 52
# ## Resources and References
#
# - [MovieLens Latest Datasets](https://grouplens.org/datasets/movielens/latest/)
# - [IMDb Non-Commercial Datasets](https://developer.imdb.com/non-commercial-datasets/)
# - [TMDB Movie Watch Providers API](https://developer.themoviedb.org/reference/movie-watch-providers)
# - [pandas documentation](https://pandas.pydata.org/docs/)
# - [Matplotlib documentation](https://matplotlib.org/stable/)
# - [Seaborn documentation](https://seaborn.pydata.org/)

# %%
# Cell 53
# Run in the notebook: jupyter nbconvert --to python source.ipynb

