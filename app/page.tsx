"use client"

import { useState } from "react"
import { SearchBar } from "@/components/search-bar"
import { MovieHero } from "@/components/movie-hero"
import { RecommendationsGrid } from "@/components/recommendations-grid"
import { Film } from "lucide-react"

export default function Home() {
  const [matchedMovie, setMatchedMovie] = useState<any>(null)
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async (movieName: string) => {
    setIsLoading(true)
    try {
      // First, search for the movie
      const searchResponse = await fetch(`/api/search?q=${encodeURIComponent(movieName)}`)
      const searchData = await searchResponse.json()

      if (searchData.error) {
        console.error("Search Error:", searchData.error)
        return
      }

      // Get the closest match from search results
      const closestMatch = searchData[0]
      if (closestMatch) {
        setMatchedMovie({
          title: closestMatch.title,
          genres: closestMatch.genres,
          rating: closestMatch.rating,
          poster: closestMatch.poster || "/placeholder.jpg",
          year: closestMatch.year
        })

        // Then get recommendations for the matched movie
        const recResponse = await fetch(`/api/recommend?movie=${encodeURIComponent(closestMatch.title)}`)
        const recData = await recResponse.json()

        if (recData.error) {
          console.error("Recommendation Error:", recData.error)
          return
        }

        if (recData.recommendations) {
          setRecommendations(recData.recommendations.map((rec: any) => ({
            ...rec,
            poster: rec.poster || "/placeholder.jpg"
          })))
        }
      }
    } catch (error) {
      console.error("Failed to fetch movie data:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Film className="h-8 w-8 text-primary" />
              <h1 className="font-serif text-2xl font-bold tracking-tight">CineMatch</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-12 md:py-20">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="font-serif text-4xl font-bold tracking-tight text-balance md:text-6xl">
            Discover Your Next Favorite Film
          </h2>
          <p className="mt-6 text-lg text-muted-foreground text-pretty">
            Enter a movie you love, and we'll recommend similar films you'll enjoy based on genres, cast, and themes.
          </p>

          <div className="mt-10">
            <SearchBar onSearch={handleSearch} isLoading={isLoading} />
          </div>
        </div>
      </section>

      {/* Matched Movie */}
      {matchedMovie && (
        <section className="container mx-auto px-4 py-12">
          <MovieHero movie={matchedMovie} onSearch={handleSearch} />
        </section>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <section className="container mx-auto px-4 py-12">
          <h3 className="mb-8 font-serif text-3xl font-bold tracking-tight">Recommended For You</h3>
          <RecommendationsGrid recommendations={recommendations} onMovieClick={handleSearch} />
        </section>
      )}

      {/* Footer */}
      <footer className="mt-20 border-t border-border/40 bg-muted/30">
        <div className="container mx-auto px-4 py-8">
          <p className="text-center text-sm text-muted-foreground">
            Powered by TMDB dataset • Built with Next.js and Python
          </p>
        </div>
      </footer>
    </div>
  )
}
