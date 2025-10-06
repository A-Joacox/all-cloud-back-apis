import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { gatewayApi } from '../services/api'
import './MovieDetails.css'

const MovieDetails = () => {
  const { id } = useParams()
  const [movieDetails, setMovieDetails] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchMovieDetails()
  }, [id])

  const fetchMovieDetails = async () => {
    try {
      setLoading(true)
      const response = await gatewayApi.getMovieDetails(id)
      setMovieDetails(response.data.data)
    } catch (err) {
      setError('Failed to load movie details')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading movie details...</div>
  if (error) return <div className="error">{error}</div>
  if (!movieDetails) return <div className="error">Movie not found</div>

  const { movie, schedules: rawSchedules } = movieDetails
  const schedules = (rawSchedules || []).map(s => ({
    id: s.id,
    room_id: s.room_id || s.roomId || s.room_id,
    showtime: s.showtime || s.show_time || s.show_time,
    price: s.price,
    room: s.room || s.room || { name: s.room_name, screen_type: s.room?.screen_type, capacity: s.room_capacity }
  }))

  return (
    <div className="movie-details">
      <div className="container">
        <div className="movie-header">
          {/* poster removed: backend has no images; show compact header */}
          <div className="movie-card-header movie-header-small">
            <div className="movie-initials">{movie.title ? movie.title.split(' ').slice(0,2).map(w=>w[0]).join('') : 'MV'}</div>
          </div>
          <div className="movie-info">
            <h1>{movie.title}</h1>
            <div className="movie-meta">
              <span className="rating">⭐ {movie.rating}/10</span>
              <span className="duration">{movie.duration} min</span>
              <span className="genre">{movie.genre?.join(', ') || 'N/A'}</span>
            </div>
            <p className="director">Director: {movie.director}</p>
            <p className="cast">Cast: {movie.cast?.join(', ') || 'N/A'}</p>
            <p className="release-date">Release Date: {new Date(movie.releaseDate).toLocaleDateString()}</p>
            <p className="description">{movie.description}</p>
          </div>
        </div>

        <div className="schedules-section">
          <h2>Showtimes</h2>
          {schedules && schedules.length > 0 ? (
            <div className="schedules-grid">
              {schedules.map(schedule => (
                <div key={schedule.id} className="schedule-card">
                  <div className="schedule-info">
                    <h3>{schedule.room?.name || `Room ${schedule.room_id}`}</h3>
                    <p>Screen Type: {schedule.room?.screen_type || 'N/A'}</p>
                    <p>Capacity: {schedule.room?.capacity || 'N/A'}</p>
                    <p>Showtime: {new Date(schedule.showtime).toLocaleString()}</p>
                    <p>Price: ${schedule.price || 'TBD'}</p>
                  </div>
                  <Link
                    to={`/booking/${schedule.id}`}
                    className="btn-primary"
                  >
                    Book Tickets
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <p>No showtimes available for this movie.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default MovieDetails
