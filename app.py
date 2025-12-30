import pickle
import streamlit as st
import requests
import pandas as pd

# ---------------------- Poster Fetching ----------------------
@st.cache_data
def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API"""
    if not movie_id:
        return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"
    
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except requests.exceptions.RequestException:
        pass

    return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"


# ---------------------- Recommendation Logic ----------------------
def recommend(movie):
    try:
        index = movies[movies["title"] == movie].index[0]
    except IndexError:
        st.error("Movie not found in dataset.")
        return [], [], [], []

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    names, posters, years, ratings = [], [], [], []

    for i in distances[1:6]:
        row = movies.iloc[i[0]]

        names.append(row.get("title", "N/A"))
        posters.append(fetch_poster(row.get("movie_id", None)))

        release_date = row.get("release_date", None)
        if pd.notna(release_date):
            years.append(str(release_date)[:4])
        else:
            years.append(None)

        rating = row.get("vote_average", None)
        if pd.notna(rating):
            ratings.append(rating)
        else:
            ratings.append(None)

    return names, posters, years, ratings


# ---------------------- Streamlit UI ----------------------
st.set_page_config(layout="wide")
st.markdown(
    "<h1 style='text-align:center; color:#4B0082;'>🎬 Movie Recommender System</h1>",
    unsafe_allow_html=True
)
st.markdown("<hr>", unsafe_allow_html=True)

# Load artifacts
try:
    movies_dict = pickle.load(open("artifacts/movie_dict.pkl", "rb"))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open("artifacts/similarity.pkl", "rb"))
except FileNotFoundError:
    st.error("Model files not found. Run the preprocessing notebook first.")
    st.stop()

movie_list = movies["title"].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button("Show Recommendation"):
    with st.spinner("Finding recommendations..."):
        names, posters, years, ratings = recommend(selected_movie)

    if names:
        cols = st.columns(5, gap="medium")  # medium gap between cards
        for i, col in enumerate(cols):
            with col:
                # Card-like container
                st.markdown(
                    f"""
                    <div style='
                        background-color:#f0f8ff;
                        padding:15px;
                        border-radius:15px;
                        text-align:center;
                        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                    '>
                        <h4 style='color:#4B0082'>{names[i]}</h4>
                        <img src="{posters[i]}" width="150" style='border-radius:10px;'><br><br>
                        <p style='margin:0'>Year: {years[i] if years[i] else 'N/A'}</p>
                        <p style='margin:0'>Rating: {ratings[i] if ratings[i] else 'N/A'} ⭐</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
