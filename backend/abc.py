# movie_recommender_full.py

import pandas as pd
import json
from fuzzywuzzy import process
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

console = Console()

# -------------------------
# Step 1: Load datasets
# -------------------------
movies = pd.read_csv("tmdb_5000_movies.csv")
credits = pd.read_csv("tmdb_5000_credits.csv")

# Merge movies and credits on movie id
df = movies.merge(credits, left_on='id', right_on='movie_id')

# -------------------------
# Step 2: JSON parsing functions
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

# Parse relevant columns
df['genres'] = parse_json_column(df['genres'], key='name')
df['keywords'] = parse_json_column(df['keywords'], key='name')
df['production_companies'] = parse_json_column(df['production_companies'], key='name')
df['cast'] = parse_json_column(df['cast'], key='name', top_n=3)  # Top 3 actors
df['director'] = parse_json_column(df['crew'], key='name')       # Usually 1 director

# -------------------------
# Step 3: Combine features for similarity
# -------------------------
df['combined_features'] = df['genres'] + " " + df['keywords'] + " " + df['production_companies'] + " " + df['cast'] + " " + df['director']

# -------------------------
# Step 4: Compute cosine similarity
# -------------------------
cv = CountVectorizer(stop_words='english')
vectors = cv.fit_transform(df['combined_features'])
similarity = cosine_similarity(vectors)

# -------------------------
# Step 5: Recommendation function
# -------------------------
def get_movie_recommendations(movie_name, n_recommendations=3):
    all_titles = df['original_title'].tolist()
    closest_match = process.extractOne(movie_name, all_titles)[0]  # Fuzzy match
    
    movie_idx = df[df['original_title'] == closest_match].index[0]
    sim_scores = list(enumerate(similarity[movie_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    recommended = []
    for i, score in sim_scores[1:n_recommendations+1]:
        recommended.append({
            'title': df.iloc[i]['original_title'],
            'genres': df.iloc[i]['genres'],
            'rating': df.iloc[i]['vote_average'],
            'overview': df.iloc[i]['overview'],
            'release_date': df.iloc[i]['release_date'],
            'homepage': df.iloc[i]['homepage'] if pd.notna(df.iloc[i]['homepage']) else "N/A",
            'cast': df.iloc[i]['cast'],
            'director': df.iloc[i]['director']
        })
    return closest_match, recommended

# -------------------------
# Step 6: Terminal UI
# -------------------------
def main():
    console.clear()
    console.rule("[bold cyan]🎬 Movie Recommendation System 🎬[/bold cyan]")
    
    while True:
        movie_name = Prompt.ask("\nEnter a movie name (or type 'exit' to quit)")
        if movie_name.lower() == 'exit':
            console.print("\nThanks for using the Movie Recommender! 👋", style="bold green")
            break
        
        try:
            closest_match, recommendations = get_movie_recommendations(movie_name)
            console.print(f"\nClosest match found: [bold yellow]{closest_match}[/bold yellow]\n")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Title", style="cyan")
            table.add_column("Genres", style="green")
            table.add_column("Rating", style="yellow")
            table.add_column("Overview", style="white", width=50)
            table.add_column("Release Date", style="blue")
            table.add_column("Homepage", style="magenta")
            table.add_column("Cast", style="white", width=30)
            table.add_column("Director", style="bright_cyan")

            for rec in recommendations:
                table.add_row(
                    rec['title'],
                    rec['genres'],
                    str(rec['rating']),
                    rec['overview'],
                    rec['release_date'],
                    rec['homepage'],
                    rec['cast'],
                    rec['director']
                )
            console.print(table)

        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}. Please try another movie.")

# -------------------------
# Step 7: Run
# -------------------------
if __name__ == "__main__":
    main()
