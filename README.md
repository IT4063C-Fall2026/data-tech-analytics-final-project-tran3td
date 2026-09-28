# Project Title
StreamHaven: Analyzing Streaming Fragmentation

## Project Overview
StreamHaven is a data analysis project focused on understanding how popular and highly rated movies are distributed across U.S. subscription-based streaming platforms. The project combines movie information, ratings, popularity measurements, and watch-provider availability from MovieLens, IMDb, and TMDB.

The analysis will identify which providers offer the most selected movies, how often movies appear on multiple services, which genres have the strongest availability, and whether highly rated or popular movies are offered by more providers. The findings could support the continued development of StreamHaven as a centralized tool that helps viewers find where movies are available.

## Self Assessment and Reflection

<!-- Edit the following section with your self assessment and reflection -->

### Self Assessment
<!-- Replace the (...) with your score -->

| Category          | Score    |
| ----------------- | -------- |
| **Setup**         | 10 / 10 |
| **Execution**     | 18 / 20 |
| **Documentation** | 10 / 10 |
| **Presentation**  | 27 / 30 |
| **Total**         | 65 / 70 |

### Reflection
<!-- Edit the following section with your reflection -->

#### What went well?
I successfully narrowed StreamHaven into a focused and measurable data analysis project about streaming fragmentation. I identified three relevant data sources from two source types: MovieLens and IMDb as file sources and TMDB as an API source. I also established how the datasets can be connected through the movieId, imdbId, tconst, and tmdbId fields.

I successfully configured the project's Pipenv environment, imported the datasets, tested the TMDB API connection, combined the data, and saved the resulting datasets as CSV files. The project questions and proposed visualizations provide a clear direction for the analysis.

#### What did not go well?
Setting up the Python environment and TMDB API took longer than expected. I initially encountered missing imports, difficulty entering the API token, and a 404 response for a TMDB movie identifier that was no longer available. I revised the code to skip unavailable TMDB records instead of allowing one missing record to stop the entire import.

For this checkpoint, I used a smaller sample of movies to test the import and merging process. The full project will require expanding the sample while continuing to handle missing or incomplete provider information.

#### What did you learn?
I learned how to import and combine data from CSV files, a compressed TSV file, and an API. I also learned how MovieLens identifiers can connect movie information to IMDb ratings and TMDB watch-provider records. This assignment showed me that real-world datasets may contain outdated or missing identifiers, so code should anticipate errors and handle them appropriately.

I also gained more experience using Pipenv, Jupyter Notebooks, pandas, HTTP requests, API authentication, Git, and GitHub.

#### What would you do differently next time?
I would configure and test the virtual environment and API access earlier so that I could spend more time examining the data. I would also begin with a very small test sample before running requests for the larger dataset. Finally, I would build error handling into the API-import code from the beginning and commit my work at more frequent checkpoints.

---

## Getting Started
### Installing Dependencies

To ensure that you have all the dependencies installed, and that we can have a reproducible environment, we will be using `pipenv` to manage our dependencies. `pipenv` is a tool that allows us to create a virtual environment for our project, and install all the dependencies we need for our project. This ensures that we can have a reproducible environment, and that we can all run the same code.

```bash
pipenv install
```

This sets up a virtual environment for our project, and installs the following dependencies:

- `ipykernel`
- `jupyter`
- `notebook`
- `black`
  Throughout your analysis and development, you will need to install additional packages. You can can install any package you need using `pipenv install <package-name>`. For example, if you need to install `numpy`, you can do so by running:

```bash
pipenv install numpy
```

This will update update the `Pipfile` and `Pipfile.lock` files, and install the package in your virtual environment.

## Helpful Resources:
* [Markdown Syntax Cheatsheet](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
* [Dataset options](https://it4063c.github.io/guides/datasets)