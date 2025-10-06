import { Link } from 'react-router-dom'
import './MovieCard.css'

const MovieCard = ({ movie }) => {
  return (
    <Link to={`/movie/${movie._id}`} className="movie-card">
      <div className="movie-card-poster">
        <div className="movie-initials">
          {movie.title ? movie.title.split(' ').slice(0,2).map(w=>w[0]).join('').toUpperCase() : 'MV'}
        </div>
      </div>
      <div className="movie-card-info">
        <h3 className="movie-title">{movie.title}</h3>
        <div className="movie-meta">
          <span className="movie-rating">⭐ {movie.rating}</span>
          <span className="movie-duration">{movie.duration}m</span>
        </div>
        <p className="movie-genre">{movie.genre?.join(', ') || 'N/A'}</p>
      </div>
    </Link>
  )
}

export default MovieCard
