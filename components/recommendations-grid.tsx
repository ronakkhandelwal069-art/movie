"use client"

import { MovieCard } from "@/components/movie-card"

interface Recommendation {
  title: string
  genres: string
  rating: number
  overview?: string
  releaseDate?: string
  homepage?: string
  cast?: string
  director?: string
  poster: string
  similarity?: number
}

interface RecommendationsGridProps {
  recommendations: Recommendation[]
  onMovieClick: (movieName: string) => void
}

export function RecommendationsGrid({ recommendations, onMovieClick }: RecommendationsGridProps) {
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {recommendations.map((movie, index) => (
        <MovieCard key={index} movie={movie} onClick={() => onMovieClick(movie.title)} />
      ))}
    </div>
  )
}
