import { Routes, Route } from 'react-router-dom'
import './App.css'
import MoviesList from './pages/MoviesList'
import MovieDetails from './pages/MovieDetails'
import Booking from './pages/Booking'
import Reservations from './pages/Reservations'
import Header from './components/Header'

function App() {
  return (
    <div className="App">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<MoviesList />} />
          <Route path="/movie/:id" element={<MovieDetails />} />
          <Route path="/booking/:scheduleId" element={<Booking />} />
          <Route path="/reservations" element={<Reservations />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
