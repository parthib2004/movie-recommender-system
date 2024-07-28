import streamlit as st
import pickle
import pandas as pd
import requests

# Replace with your Trakt API key
TRAKT_API_KEY = 'c24ec212df4197744517f1241f8172a8'
TRAKT_API_URL = 'https://api.trakt.tv'

# TMDb API Key
TMDB_API_KEY = '820111dfff08c34f7c23aec54164cb39'
TMDB_API_URL = 'https://api.themoviedb.org/3'


def fetch_poster_from_tmdb(tmdb_id):
    url = f'{TMDB_API_URL}/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language=en-US'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_poster_path = "https://image.tmdb.org/t/p/w500" + poster_path
            return full_poster_path
    print(f"TMDb fetch failed for {tmdb_id}, response: {response.text}")
    return None


def fetch_tmdb_id_from_trakt(movie_id):
    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': TRAKT_API_KEY
    }
    url = f'{TRAKT_API_URL}/search/trakt/{movie_id}?type=movie'
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        movie_data = response.json()[0]['movie']
        tmdb_id = movie_data.get('ids', {}).get('tmdb')
        return tmdb_id
    print(f"Trakt fetch failed for {movie_id}, response: {response.text}")
    return None


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        movie_title = movies.iloc[i[0]].title

        recommended_movies.append(movie_title)
        # Fetch TMDb ID from Trakt API and then fetch poster from TMDb API
        tmdb_id = fetch_tmdb_id_from_trakt(movie_id)
        print(f"Movie: {movie_title}, TMDb ID: {tmdb_id}")
        if tmdb_id:
            poster_url = fetch_poster_from_tmdb(tmdb_id)
            recommended_movies_posters.append(poster_url)
            print(f"Poster URL: {poster_url}")
        else:
            recommended_movies_posters.append(None)

    return recommended_movies, recommended_movies_posters


movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie:",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    for i in range(len(names)):
        with st.container():
            st.text(names[i])
            if posters[i]:
                st.image(posters[i])
            else:
                st.text("")


