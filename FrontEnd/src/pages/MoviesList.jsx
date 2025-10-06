import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { moviesApi } from '../services/api'
import MovieCard from '../components/MovieCard'
import './MoviesList.css'

const MoviesList = () => {
  const [movies, setMovies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [genre, setGenre] = useState('')
  const [genres, setGenres] = useState([])
  const [pagination, setPagination] = useState({})
  const [username] = useState('Cinephile') // You can make this dynamic based on user

  useEffect(() => {
    fetchMovies()
  }, [search, genre])

  useEffect(() => {
    fetchGenres()
  }, [])

  const fetchMovies = async (page = 1) => {
    try {
      setLoading(true)
      const params = { page, limit: 12 }
      if (search) params.search = search
      if (genre) params.genre = genre

      console.log('Fetching movies with params:', params)
      const response = await moviesApi.getMovies(params)
      console.log('Movies API response:', response)
      console.log('Response data:', response.data)

      // Handle different response structures
      let moviesData = []
      let paginationData = {}

      if (response.data) {
        if (response.data.data && Array.isArray(response.data.data)) {
          moviesData = response.data.data
          paginationData = response.data.pagination || {}
        } else if (Array.isArray(response.data)) {
          moviesData = response.data
        } else if (response.data.movies) {
          moviesData = response.data.movies
        }
      }

      console.log('Parsed movies data:', moviesData)
      setMovies(moviesData)
      setPagination(paginationData)
    } catch (err) {
      console.error('Error fetching movies:', err)
      setError(`Failed to load movies: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const fetchGenres = async () => {
    try {
      const response = await moviesApi.getGenres()
      console.log('Genres API response:', response)
      
      let genresData = []
      if (response.data) {
        if (response.data.data && Array.isArray(response.data.data)) {
          genresData = response.data.data
        } else if (Array.isArray(response.data)) {
          genresData = response.data
        }
      }
      
      setGenres(genresData)
    } catch (err) {
      console.error('Failed to load genres', err)
      // Don't set error state for genres, just log it
      setGenres([]) // Set empty array so the filter still works
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    fetchMovies()
  }

  // Group movies by rating for different sections
  const highRatedMovies = movies.filter(m => m.rating >= 8)
  const popularMovies = movies.filter(m => m.rating >= 7 && m.rating < 8)
  const recentMovies = movies.slice(0, 6)

  if (loading) return <div className="loading">Loading movies...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="movies-list">
      {/* Hero Header */}
      <div className="hero-header">
        <div className="hero-content">
            <div className="hero-filters">
            <form onSubmit={handleSearch} className="search-form">
              <input
                type="text"
                placeholder="🔍 Search titles..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </form>
            
            <select value={genre} onChange={(e) => setGenre(e.target.value)} className="genre-select">
              <option value="">All Genres</option>
              {genres.map(g => (
                <option key={g._id} value={g.name}>{g.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Continue Watching Section */}
      {recentMovies.length > 0 && (
        <div className="content-section">
          <h2 className="section-title">Recommended</h2>
          <div className="horizontal-scroll">
            {recentMovies.map(movie => (
              <MovieCard key={movie._id} movie={movie} />
            ))}
          </div>
        </div>
      )}

      {/* High Rated Section */}
      {highRatedMovies.length > 0 && (
        <div className="content-section">
          <h2 className="section-title">Top Rated Movies</h2>
          <div className="horizontal-scroll">
            {highRatedMovies.map(movie => (
              <MovieCard key={movie._id} movie={movie} />
            ))}
          </div>
        </div>
      )}

      {/* Popular Section */}
      {popularMovies.length > 0 && (
        <div className="content-section">
          <h2 className="section-title">Popular Right Now</h2>
          <div className="horizontal-scroll">
            {popularMovies.map(movie => (
              <MovieCard key={movie._id} movie={movie} />
            ))}
          </div>
        </div>
      )}

      {/* All Movies Section */}
      <div className="content-section">
        <h2 className="section-title">All Movies</h2>
        <div className="horizontal-scroll">
          {movies.map(movie => (
            <MovieCard key={movie._id} movie={movie} />
          ))}
        </div>
      </div>

      {/* Pagination */}
      {pagination.pages > 1 && (
        <div className="pagination">
          <button
            onClick={() => fetchMovies(pagination.page - 1)}
            disabled={pagination.page === 1}
            className="pagination-btn"
          >
            ← Previous
          </button>
          <span className="pagination-info">
            Page {pagination.page} of {pagination.pages}
          </span>
          <button
            onClick={() => fetchMovies(pagination.page + 1)}
            disabled={pagination.page === pagination.pages}
            className="pagination-btn"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}

export default MoviesList
