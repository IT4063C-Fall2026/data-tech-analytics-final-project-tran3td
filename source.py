#!/usr/bin/env python
# coding: utf-8

# # {Project Title}
StreamHaven: Analyzing Streaming Fragmentation
# 
# ![Banner](./assets/banner.jpeg)

# ## Topic
# *What problem are you (or your stakeholder) trying to address?*
# 📝 <!-- Answer Below -->
Streaming content is divided across many different platforms. Viewers may have difficulty finding a movie or may need multiple subscriptions to access the movies they want. Titles may also move between platforms or become unavailable. This fragmentation can make streaming confusing, inconvenient, and expensive.

My project will analyze the availability of popular and highly rated movies across U.S. streaming platforms. The results could help guide the continued development of StreamHaven, a centralized platform where users can search for movies and see where they are available.

To keep the project manageable, I will focus on movies available in the United States through subscription-based streaming services. I will begin with approximately 250–500 movies that have received enough ratings to provide reliable comparisons.

This design incorporates feedback from my original project discussion by narrowing the project from the broad idea of studying streaming prices, user behavior, and content removal to a more specific question that can be answered with available data: How fragmented are popular movies across streaming services?

# ## Project Question
# *What specific question are you seeking to answer with this project?*
# *This is not the same as the questions you ask to limit the scope of the project.*
# 📝 <!-- Answer Below -->
Which streaming providers offer the largest number of popular and highly rated movies?

How many subscription services are typically required to access the selected movies?

What percentage of the selected movies are available on more than one subscription service?

Which movie genres are the most and least available across streaming platforms?

Is there a relationship between a movie's rating or popularity and the number of streaming platforms offering it?

Which movies are unavailable through any of the subscription services represented in the data?

# ## What would an answer look like?
# *What is your hypothesized answer to your question?*
# 📝 <!-- Answer Below -->
A bar chart comparing the number of selected movies available on each streaming service.

A histogram showing the number of streaming providers available per movie.

A stacked bar chart comparing streaming availability across movie genres.

A scatter plot comparing IMDb ratings or vote counts with the number of available providers.

A table showing highly rated movies, their genres, ratings, and available streaming services.

A summary stating how many platforms would be needed to cover the greatest number of selected movies.

# ## Data Sources
# *What 3 data sources have you identified for this project?*
# *How are you going to relate these datasets?*
# 📝 <!-- Answer Below -->
1. MovieLens Dataset — File Source

The MovieLens dataset provides movies.csv, ratings.csv, and links.csv. It contains movie titles, genres, user ratings, and identifiers that connect movies to IMDb and TMDB.

Important variables include:

movieId

title

genres

rating

imdbId

tmdbId

Source: MovieLens Latest Datasets

2. IMDb Non-Commercial Dataset — File Source

The IMDb ratings dataset provides an IMDb title identifier, average rating, and number of votes. The number of votes will help me select movies with enough audience activity, while the average rating will help identify highly rated movies.

Important variables include:

tconst

averageRating

numVotes

Source: IMDb Title Ratings Dataset

3. TMDB Watch Providers — API Source

The TMDB API provides watch-provider availability for individual movies. I will use it to identify which services offer each movie in the United States and whether each movie is available through a subscription, free service, rental, or purchase.

Important variables include:

tmdbId

Country code

Provider ID

Provider name

Availability type

Source: TMDB Movie Watch Providers API

How the Data Sources Relate

MovieLens will serve as the bridge between all three sources:

movieId connects movies.csv, ratings.csv, and links.csv.

links.csv contains imdbId, which can be formatted as an IMDb tconst value and joined with the IMDb ratings dataset.

links.csv also contains tmdbId, which can be used to request watch-provider information from the TMDB API.

After combining the data, each movie can contain its title, genre, MovieLens ratings, IMDb rating and vote count, TMDB identifier, and U.S. streaming providers.

# ## Approach and Analysis
# *What is your approach to answering your project question?*
# *How will you use the identified data to answer your project question?*
# 📝 <!-- Start Discussing the project here; you can add as many code cells as you need -->

I will first import the MovieLens files, IMDb ratings dataset, and TMDB watch-provider data. MovieLens will provide the primary movie list and identifiers used to connect the three sources. I will use IMDb vote counts and ratings to select popular and highly rated movies with sufficient audience activity.

The analysis will focus on approximately 250–500 movies. For the initial checkpoint import, I used a smaller sample to test the API connection and data-merging process. TMDB records that cannot be found will be documented and skipped instead of stopping the import.

After combining the sources, I will examine provider coverage, the number of providers per movie, differences among genres, and the relationship between movie popularity and streaming availability. The final results will be presented using charts, summary statistics, and tables.

# In[5]:


from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from getpass import getpass

import pandas as pd
import requests

data_folder = Path("data")
data_folder.mkdir(exist_ok=True)

print("Setup complete")


# In[10]:


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


# In[12]:


links["tconst"] = (
    "tt"
    + links["imdbId"].astype("Int64").astype(str).str.zfill(7)
)

movielens_data = movies.merge(
    links,
    on="movieId",
    how="left"
)

movielens_data.head()


# In[14]:


imdb_url = "https://datasets.imdbws.com/title.ratings.tsv.gz"

imdb_ratings = pd.read_csv(
    imdb_url,
    sep="\t",
    compression="gzip",
    na_values="\\N"
)

print("IMDb ratings:", imdb_ratings.shape)
imdb_ratings.head()


# In[16]:


movie_data = movielens_data.merge(
    imdb_ratings,
    on="tconst",
    how="left"
)

print("Combined MovieLens and IMDb:", movie_data.shape)
movie_data.head()


# In[18]:


project_movies = (
    movie_data
    .dropna(subset=["tmdbId", "averageRating", "numVotes"])
    .query("numVotes >= 25000")
    .sort_values(
        ["averageRating", "numVotes"],
        ascending=False
    )
    .head(25)
    .copy()
)

project_movies["tmdbId"] = project_movies["tmdbId"].astype(int)

print("Selected movies:", project_movies.shape)
project_movies.head()


# In[21]:


tmdb_token = getpass("Paste your TMDB API Read Access Token: eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NDNlNmRjNmI0YmZjYmIwM2RiMTM5NDAwYzA1YzY4NSIsIm5iZiI6MTc5MDU2Mjk3MS43NTAwMDAyLCJzdWIiOiI2YWI5ZDI5YjFhNWY2OTgxYWExYjcwMGYiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.-emWTtmlZeRpVcNgSzTEj8zz58QFIVxN_Per_u4ALvc")

tmdb_headers = {
    "Authorization": f"Bearer {tmdb_token}",
    "accept": "application/json"
}

print("TMDB token received")


# In[23]:


test_movie_id = int(project_movies.iloc[0]["tmdbId"])

test_url = (
    f"https://api.themoviedb.org/3/movie/"
    f"{test_movie_id}/watch/providers"
)

test_response = requests.get(
    test_url,
    headers=tmdb_headers,
    timeout=30
)

print("Status code:", test_response.status_code)


# In[26]:


provider_records = []
missing_movies = []

for tmdb_id in project_movies["tmdbId"]:
    url = (
        f"https://api.themoviedb.org/3/movie/"
        f"{tmdb_id}/watch/providers"
    )

    response = requests.get(
        url,
        headers=tmdb_headers,
        timeout=30
    )

    # Skip movie IDs that TMDB cannot find
    if response.status_code == 404:
        missing_movies.append(tmdb_id)
        continue

    response.raise_for_status()

    us_results = response.json().get("results", {}).get("US", {})

    for access_type in ["flatrate", "free", "ads", "rent", "buy"]:
        providers = us_results.get(access_type, [])

        for provider in providers:
            provider_records.append({
                "tmdbId": tmdb_id,
                "provider_id": provider["provider_id"],
                "provider_name": provider["provider_name"],
                "access_type": access_type,
                "country": "US"
            })

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
print("Missing TMDB movie IDs:", missing_movies)

watch_providers.head()


# In[29]:


subscription_providers = watch_providers[
    watch_providers["access_type"] == "flatrate"
].copy()

analysis_data = project_movies.merge(
    subscription_providers,
    on="tmdbId",
    how="left"
)

print("Final combined dataset:", analysis_data.shape)
analysis_data.head()


# In[31]:


project_movies.to_csv(
    data_folder / "project_movies.csv",
    index=False
)

watch_providers.to_csv(
    data_folder / "watch_providers.csv",
    index=False
)

analysis_data.to_csv(
    data_folder / "streamhaven_analysis_data.csv",
    index=False
)

print("Files saved successfully in the data folder")


# In[33]:


print("MovieLens movie records:", len(movies))
print("IMDb rating records:", len(imdb_ratings))
print("TMDB provider records:", len(watch_providers))
print("Final combined records:", len(analysis_data))


# ## Resources and References
# *What resources and references have you used for this project?*
# 📝 <!-- Answer Below -->

# In[34]:


# ⚠️ Make sure you run this cell at the end of your notebook before every submission!
get_ipython().system('jupyter nbconvert --to python source.ipynb')

