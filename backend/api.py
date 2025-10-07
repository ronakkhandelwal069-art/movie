from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
from fuzzywuzzy import process
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

app = Flask(__name__)
CORS(app)

print("Starting Flask server...")

# -------------------------
# Load datasets
# -------------------------
def load_data():
    try:
        print("Loading movie datasets...")
        movies = pd.read_csv("tmdb_5000_movies.csv")
        credits = pd.read_csv("tmdb_5000_credits.csv")
        print("Merging datasets...")
        df = movies.merge(credits, left_on='id', right_on='movie_id')
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None

# -------------------------
# JSON parsing
# -------------------------
def parse_json_column(col, key=None, top_n=None):
    parsed = []
    for item in col:
        try:
            if pd.isna(item):
                parsed.append("")
                continue
            data = json.loads(str(item).replace("'", '"'))
            if isinstance(data, list):
                if key:
                    data = [d.get(key, '') for d in data]
                if top_n:
                    data = data[:top_n]
                parsed.append(" ".join(filter(None, data)))
            else:
                parsed.append(str(data))
        except:
            parsed.append("")
    return parsed

# Load data
df = load_data()

if df is not None:
    print("Processing movie data...")
    # Process columns
    df['genres'] = parse_json_column(df['genres'], key='name')
    df['keywords'] = parse_json_column(df['keywords'], key='name')
    df['production_companies'] = parse_json_column(df['production_companies'], key='name')
    df['cast'] = parse_json_column(df['cast'], key='name', top_n=3)
    
    # Extract director from crew
    def get_director(crew_data):
        try:
            crew = json.loads(str(crew_data).replace("'", '"'))
            directors = [member['name'] for member in crew if member['job'] == 'Director']
            return ' '.join(directors) if directors else ''
        except:
            return ''
    
    df['director'] = df['crew'].apply(get_director)
    
    # Combine features for similarity calculation
    df['combined_features'] = df['genres'].fillna('') + ' ' + \
                             df['keywords'].fillna('') + ' ' + \
                             df['production_companies'].fillna('') + ' ' + \
                             df['cast'].fillna('') + ' ' + \
                             df['director'].fillna('')

    # Add poster URL if available
    df['poster_url'] = "https://image.tmdb.org/t/p/w500" + df['poster_path'].fillna("")

    # Compute similarity
    print("Computing similarity matrix...")
    cv = CountVectorizer(stop_words='english')
    vectors = cv.fit_transform(df['combined_features'])
    similarity = cosine_similarity(vectors)
    print("Setup complete!")
else:
    print("Failed to load movie data!")
    similarity = None

# -------------------------
# API endpoints
# -------------------------
@app.route('/api/search', methods=['GET'])
def search_movies():
    if df is None:
        return jsonify({'error': 'Movie database not loaded'}), 500

    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    try:
        all_titles = df['original_title'].tolist()
        matches = process.extract(query, all_titles, limit=5)
        results = []
        
        for title, score in matches:
            movie = df[df['original_title'] == title].iloc[0]
            results.append({
                'title': title,
                'genres': movie['genres'],
                'poster': movie['poster_url'],
                'rating': float(movie['vote_average']) if pd.notna(movie['vote_average']) else None,
                'year': movie['release_date'][:4] if pd.notna(movie['release_date']) else None,
                'score': score
            })
        
        return jsonify(results)
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': f'Error searching movies: {str(e)}'}), 500

@app.route('/api/recommend', methods=['GET'])
def get_recommendations():
    if df is None or similarity is None:
        return jsonify({'error': 'Movie database not loaded'}), 500

    movie_name = request.args.get('movie', '')
    if not movie_name:
        return jsonify({'error': 'Movie name is required'}), 400
    
    try:
        all_titles = df['original_title'].tolist()
        closest_match = process.extractOne(movie_name, all_titles)
        if not closest_match or closest_match[1] < 60:  # If match score is less than 60%
            return jsonify({'error': 'Movie not found'}), 404
            
        movie_idx = df[df['original_title'] == closest_match[0]].index[0]
        sim_scores = list(enumerate(similarity[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        recommended = []
        for i, score in sim_scores[1:7]:  # Get top 6 recommendations
            movie_data = df.iloc[i]
            recommended.append({
                'title': movie_data['original_title'],
                'genres': movie_data['genres'],
                'rating': float(movie_data['vote_average']) if pd.notna(movie_data['vote_average']) else None,
                'overview': movie_data['overview'] if pd.notna(movie_data['overview']) else None,
                'releaseDate': movie_data['release_date'] if pd.notna(movie_data['release_date']) else None,
                'homepage': movie_data['homepage'] if pd.notna(movie_data['homepage']) else None,
                'cast': movie_data['cast'],
                'director': movie_data['director'],
                'poster': movie_data['poster_url'],
                'similarity': float(score)
            })
        
        return jsonify({
            'match': closest_match[0],
            'matchScore': closest_match[1],
            'recommendations': recommended
        })
    except Exception as e:
        print(f"Recommendation error: {str(e)}")
        return jsonify({'error': f'Error getting recommendations: {str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'status': 'ok',
        'database_loaded': df is not None,
        'similarity_computed': similarity is not None,
        'movie_count': len(df) if df is not None else 0
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)