"use client"

import { Star, Calendar, User, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface MovieHeroProps {
  movie: {
    title: string
    genres: string
    rating: number
    year?: string
    poster?: string
  }
  onSearch: (movieName: string) => void
}

export function MovieHero({ movie, onSearch }: MovieHeroProps) {
  const genres = movie.genres.split(" ").filter(Boolean)

  return (
    <div className="overflow-hidden rounded-xl border border-border/40 bg-card">
      <div className="grid gap-8 md:grid-cols-[300px_1fr] lg:grid-cols-[400px_1fr]">
        {/* Poster */}
        <div className="relative aspect-[2/3] overflow-hidden bg-muted md:aspect-auto">
          <img
            src={
              movie.poster ||
              `/placeholder.svg?height=600&width=400&query=${encodeURIComponent(movie.title)}+poster`
            }
            alt={movie.title}
            className="h-full w-full object-cover"
          />
        </div>

        {/* Details */}
        <div className="flex flex-col justify-center p-8 lg:p-12">
          <Badge variant="secondary" className="mb-4 w-fit">
            Matched Movie
          </Badge>

          <h2 className="font-serif text-4xl font-bold tracking-tight text-balance lg:text-5xl">{movie.title}</h2>

          {/* Meta Info */}
          <div className="mt-6 flex flex-wrap items-center gap-4 text-sm">
            <div className="flex items-center gap-1.5">
              <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
              <span className="font-semibold">{movie.rating.toFixed(1)}</span>
            </div>

            {movie.year && (
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span>{movie.year}</span>
              </div>
            )}
          </div>

          {/* Genres */}
          <div className="mt-4 flex flex-wrap gap-2">
            {genres.map((genre, index) => (
              <Badge key={index} variant="outline">
                {genre}
              </Badge>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
