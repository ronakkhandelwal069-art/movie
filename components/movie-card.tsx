"use client"

import { Star, Calendar, TrendingUp } from "lucide-react"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface MovieCardProps {
  movie: {
    title: string
    genres: string
    rating: number
    overview?: string
    releaseDate?: string
    cast?: string
    director?: string
    poster: string
    similarity?: number
  }
  onClick: () => void
}

export function MovieCard({ movie, onClick }: MovieCardProps) {
  const genres = movie.genres.split(" ").filter(Boolean).slice(0, 3)

  return (
    <Card className="group overflow-hidden transition-all hover:shadow-lg cursor-pointer" onClick={onClick}>
      {/* Poster */}
      <div className="relative aspect-[2/3] overflow-hidden bg-muted">
        <img
          src={movie.poster || `/placeholder.svg?height=600&width=400&query=${encodeURIComponent(movie.title)}+poster`}
          alt={movie.title}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />

        {/* Similarity Score Badge */}
        {movie.similarity && (
          <div className="absolute right-3 top-3">
            <Badge className="gap-1 bg-background/90 backdrop-blur">
              <TrendingUp className="h-3 w-3" />
              {Math.round(movie.similarity * 100)}% Match
            </Badge>
          </div>
        )}
      </div>

      <CardContent className="p-5">
        {/* Title */}
        <h3 className="font-serif text-xl font-bold tracking-tight text-balance line-clamp-2">{movie.title}</h3>

        {/* Meta Info */}
        <div className="mt-3 flex items-center gap-3 text-sm">
          <div className="flex items-center gap-1">
            <Star className="h-3.5 w-3.5 fill-yellow-500 text-yellow-500" />
            <span className="font-semibold">{movie.rating.toFixed(1)}</span>
          </div>

          {movie.releaseDate && (
            <div className="flex items-center gap-1 text-muted-foreground">
              <Calendar className="h-3.5 w-3.5" />
              <span>{new Date(movie.releaseDate).getFullYear()}</span>
            </div>
          )}
        </div>

        {/* Genres */}
        <div className="mt-3 flex flex-wrap gap-1.5">
          {genres.map((genre, index) => (
            <Badge key={index} variant="secondary" className="text-xs">
              {genre}
            </Badge>
          ))}
        </div>

        {/* Overview */}
        {movie.overview && (
          <p className="mt-3 text-sm text-muted-foreground leading-relaxed line-clamp-3">{movie.overview}</p>
        )}

        {/* Cast */}
        {movie.cast && (
          <div className="mt-4 border-t border-border/40 pt-4">
            <p className="text-xs font-medium text-muted-foreground">Cast</p>
            <p className="mt-1 text-sm line-clamp-1">{movie.cast}</p>
          </div>
        )}

        {/* Director */}
        {movie.director && (
          <div className="mt-2">
            <p className="text-xs font-medium text-muted-foreground">Director</p>
            <p className="mt-1 text-sm line-clamp-1">{movie.director}</p>
          </div>
        )}
      </CardContent>

      <CardFooter className="p-5 pt-0">
        <Button variant="outline" className="w-full bg-transparent" onClick={onClick}>
          Get Recommendations
        </Button>
      </CardFooter>
    </Card>
  )
}
