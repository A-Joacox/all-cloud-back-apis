Resumen de endpoints usados por el FrontEnd

Base VM: http://3.86.188.48 (puertos 3001..3004 proxy configurado en vite.config.js)

Movies API (http://3.86.188.48:3001)
- GET /api/movies
  Response: { success: true, data: [movie], pagination: { page, limit, total, pages } }
- GET /api/movies/:id
  Response: { success: true, data: movie }
- GET /api/genres
  Response: { success: true, data: [genres] }
- GET /api/movies/featured, /api/movies/search
  Response: similar to GET /api/movies

Rooms API (http://3.86.188.48:3002)
- GET /api/rooms
  Response: { success: true, data: [rooms] } OR sometimes { data: [...], success: true }
- GET /api/rooms/:id
  Response: { success: true, data: room }
- GET /api/rooms/:id/seats
  Response: { success: true, data: [seats] }
- GET /api/schedules?movie_id=...&room_id=...
  Response: { success: true, data: [schedules] }
  Each schedule: { id, movie_id, room_id, show_time (iso), price, is_active, room_name }
  Note: show_time field name differs from frontend expected "showtime" -> frontend normalizes.

Reservations API (http://3.86.188.48:3003)
- GET /api/reservations
  Response: ApiResponse wrapper: { success: true, data: [reservations] }
- GET /api/reservations/user/:userId
  Response: { success: true, data: [reservations] }
- POST /api/reservations
  Request body: { userId, scheduleId, movieId, seatIds, totalAmount }
  Response: { success: true, data: reservation }
- GET /api/users
  Response: { success: true, data: [users] }

Gateway API (http://3.86.188.48:3004)
- GET /api/showtimes?movieId=...&roomId=... -> orchestrated showtimes
  Response: { success: true, data: [enrichedSchedules] }
- GET /api/movie-details/:movieId
  Response: { success: true, data: { movie, schedules } }
- POST /api/book-ticket
  Request body: { userId, scheduleId, movieId, seatIds, totalAmount }
  Response: 201 { success: true, data: reservation, message }

Notas:
- El FrontEnd usa proxy en vite.config.js apuntando a la VM con los puertos 3001-3004. No es necesario cambiar URLs en código si se corre con Vite.
- Algunas respuestas usan fields diferentes (show_time vs showtime). El FrontEnd fue actualizado para normalizar.
- rooms-api no implementa GET /api/schedules/:id; frontend ahora busca en /api/schedules y filtra por id (wrapper en services/api.js).

Recomendación:
- Ejecutar el frontend con `npm install` y `npm run dev` en la carpeta `FrontEnd` y probar flujos: explorar películas, ver detalles, elegir showtime, reservar.
- Si se desea, reemplazar el wrapper getSchedule por un endpoint en rooms-api que devuelva schedule por id (recomendado para performance).

UX para peticiones largas:
- Se quitó el timeout/abort en la UI para peticiones largas (antes se usaban Promise.race y timeouts).
- Ahora la UI muestra un indicador de progreso con tiempo transcurrido (segundos) mientras la petición está en curso (campo `elapsed` en `Reservations.jsx`).
- Esta UX permite que las peticiones largas terminen correctamente sin perder la respuesta del servidor.
