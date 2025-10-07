import { type NextRequest, NextResponse } from "next/server"

// Mock data for development - replace with actual API calls
const FLASK_API_URL = process.env.FLASK_API_URL || "http://localhost:5000"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const movie = searchParams.get("movie")
  const n = searchParams.get("n") || "3"

  if (!movie) {
    return NextResponse.json({ error: "Movie parameter is required" }, { status: 400 })
  }

  try {
    const response = await fetch(`${FLASK_API_URL}/api/recommend?movie=${encodeURIComponent(movie)}&n=${n}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    return NextResponse.json({
      matched_movie: {
        title: data.match,
      },
      recommendations: data.recommendations.map((rec: any) => ({
        title: rec.title,
        genres: rec.genres,
        rating: rec.rating,
        overview: rec.overview,
        releaseDate: rec.releaseDate,
        homepage: rec.homepage,
        cast: rec.cast,
        director: rec.director,
        poster: rec.poster
      }))
    })
  } catch (error) {
    console.error("Error fetching recommendations:", error)
    return NextResponse.json({ error: "Failed to fetch recommendations" }, { status: 500 })
  }
}
