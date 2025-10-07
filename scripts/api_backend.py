"""
Flask API Backend for Movie Recommendation System
Exposes the Python recommendation function as REST API endpoints
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import json
from fuzzywuzzy import process
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Global variables for data
df = None
similarity = None

def parse_json_column(col, key=None, top_n=None):
    """Parse JSON columns from TMDB dataset"""
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

def initialize_data():
    """Load and process movie datasets"""
    global df, similarity
    
    print("Loading datasets...")
    movies = pd.read_csv("tmdb_5000_movies.csv")
    credits = pd.read_csv("tmdb_5000_credits.csv")
    
    # Merge datasets
    df = movies.merge(credits, left_on='id', right_on='movie_id')
    
    # Parse JSON columns
    df['genres'] = parse_json_column(df['genres'], key='name')
    df['keywords'] = parse_json_column(df['keywords'], key='name')
    df['production_companies'] = parse_json_column(df['production_companies'], key='name')
    df['cast'] = parse_json_column(df['cast'], key='name', top_n=3)
    df['director'] = parse_json_column(df['crew'], key='name')
    
    # Get poster paths
    df['poster_path'] = df.apply(
        lambda row: f"https://image.tmdb.org/t/p/w500{json.loads(row['genres'].replace(\"'\", '\"'))[0].get('poster_path', '')}" 
        if row['genres'] else "/placeholder.svg?height=450&width=300",
        axis=1
    )
    
    # Combine features for similarity
    df['combined_features'] = (
        df['genres'] + " " + 
        df['keywords'] + " " + 
        df['production_companies'] + " " + 
        df['cast'] + " " + 
        df['director']
    )
    
    # Compute similarity matrix
    print("Computing similarity matrix...")
    cv = CountVectorizer(stop_words='english')
    vectors = cv.fit_transform(df['combined_features'])
    similarity = cosine_similarity(vectors)
    
    print("Initialization complete!")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Movie Recommender API is running"})

@app.route('/api/search', methods=['GET'])
def search_movies():
    """Search for movies by name (fuzzy matching)"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    all_titles = df['original_title'].tolist()
    matches = process.extract(query, all_titles, limit=limit)
    
    results = [{"title": match[0], "score": match[1]} for match in matches]
    return jsonify({"results": results})

@app.route('/api/recommend', methods=['GET'])
def get_recommendations():
    """Get movie recommendations based on a movie name"""
    movie_name = request.args.get('movie', '')
    n_recommendations = int(request.args.get('n', 3))
    
    if not movie_name:
        return jsonify({"error": "Query parameter 'movie' is required"}), 400
    
    try:
        # Find closest match
        all_titles = df['original_title'].tolist()
        closest_match = process.extractOne(movie_name, all_titles)[0]
        
        # Get movie index
        movie_idx = df[df['original_title'] == closest_match].index[0]
        
        # Get matched movie details
        matched_movie = df.iloc[movie_idx]
        
        # Calculate similarity scores
        sim_scores = list(enumerate(similarity[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get recommendations
        recommendations = []
        for i, score in sim_scores[1:n_recommendations+1]:
            movie = df.iloc[i]
            recommendations.append({
                'title': movie['original_title'],
                'genres': movie['genres'],
                'rating': float(movie['vote_average']),
                'overview': movie['overview'],
                'release_date': movie['release_date'],
                'homepage': movie['homepage'] if pd.notna(movie['homepage']) else None,
                'cast': movie['cast'],
                'director': movie['director'],
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if pd.notna(movie['poster_path']) else None,
                'similarity_score': float(score)
            })
        
        return jsonify({
            'matched_movie': {
                'title': matched_movie['original_title'],
                'genres': matched_movie['genres'],
                'rating': float(matched_movie['vote_average']),
                'overview': matched_movie['overview'],
                'release_date': matched_movie['release_date'],
                'homepage': matched_movie['homepage'] if pd.notna(matched_movie['homepage']) else None,
                'cast': matched_movie['cast'],
                'director': matched_movie['director'],
                'poster_url': f"https://image.tmdb.org/t/p/w500{matched_movie['poster_path']}" if pd.notna(matched_movie['poster_path']) else None
            },
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/movies', methods=['GET'])
def get_all_movies():
    """Get list of all available movies"""
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    movies = df[['original_title', 'vote_average', 'release_date']].iloc[offset:offset+limit]
    return jsonify({
        'movies': movies.to_dict('records'),
        'total': len(df)
    })

if __name__ == '__main__':
    initialize_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
