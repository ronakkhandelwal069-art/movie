# app.py

import pandas as pd
import json
import streamlit as st
from fuzzywuzzy import process
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# -------------------------
# Load datasets
# -------------------------
@st.cache_data
def load_data():
    movies = pd.read_csv("tmdb_5000_movies.csv")
    credits = pd.read_csv("tmdb_5000_credits.csv")
    df = movies.merge(credits, left_on='id', right_on='movie_id')
    return df

df = load_data()

# -------------------------
# JSON parsing
# -------------------------
def parse_json_column(col, key=None, top_n=None):
    parsed = []
    for item in col:
        try:
            data = json.loads(item.replace("'", '"'))
            if isinstance(data, list):
                if key:
                    data = [d.get(key, '') for d in data]
                if top_n:
                    data = data[:top_n]
                parsed.append(" ".join(data))
            else:
                parsed.append(str(data))
        except:
            parsed.append("")
    return parsed

df['genres'] = parse_json_column(df['genres'], key='name')
df['keywords'] = parse_json_column(df['keywords'], key='name')
df['production_companies'] = parse_json_column(df['production_companies'], key='name')
df['cast'] = parse_json_column(df['cast'], key='name', top_n=3)
df['director'] = parse_json_column(df['crew'], key='name')
df['combined_features'] = df['genres'] + " " + df['keywords'] + " " + df['production_companies'] + " " + df['cast'] + " " + df['director']

# Add poster URL if available
df['poster_url'] = "https://image.tmdb.org/t/p/w500" + df['poster_path'].fillna("")

# -------------------------
# Compute similarity
# -------------------------
cv = CountVectorizer(stop_words='english')
vectors = cv.fit_transform(df['combined_features'])
similarity = cosine_similarity(vectors)

# -------------------------
# Recommendation function
# -------------------------
def get_movie_recommendations(movie_name, n=3):
    all_titles = df['original_title'].tolist()
    closest_match = process.extractOne(movie_name, all_titles)[0]
    movie_idx = df[df['original_title'] == closest_match].index[0]
    sim_scores = list(enumerate(similarity[movie_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    recommended = []
    for i, score in sim_scores[1:n+1]:
        recommended.append({
            'Title': df.iloc[i]['original_title'],
            'Genres': df.iloc[i]['genres'],
            'Rating': df.iloc[i]['vote_average'],
            'Overview': df.iloc[i]['overview'],
            'Release Date': df.iloc[i]['release_date'],
            'Homepage': df.iloc[i]['homepage'] if pd.notna(df.iloc[i]['homepage']) else "N/A",
            'Cast': df.iloc[i]['cast'],
            'Director': df.iloc[i]['director'],
            'Poster': df.iloc[i]['poster_url']
        })
    return closest_match, recommended

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommendation System")
st.write("Enter a movie name to get recommendations based on genres, actors, director, and rating.")

movie_input = st.text_input("Enter a movie name:")

if movie_input:
    try:
        closest_match, recommendations = get_movie_recommendations(movie_input)
        st.subheader(f"Closest match found: {closest_match}")
        
        for rec in recommendations:
            col1, col2 = st.columns([1, 3])
            with col1:
                if rec['Poster'] != "https://image.tmdb.org/t/p/w500":
                    st.image(rec['Poster'], use_column_width=True)
            with col2:
                st.markdown(f"### {rec['Title']}")
                st.write(f"**Genres:** {rec['Genres']}")
                st.write(f"**Rating:** {rec['Rating']}")
                st.write(f"**Overview:** {rec['Overview']}")
                st.write(f"**Release Date:** {rec['Release Date']}")
                st.write(f"**Homepage:** {rec['Homepage']}")
                st.write(f"**Cast:** {rec['Cast']}")
                st.write(f"**Director:** {rec['Director']}")
            st.markdown("---")
    except Exception as e:
        st.error(f"Movie not found. Try another title. Error: {e}")
