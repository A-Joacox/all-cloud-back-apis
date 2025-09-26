package com.cinema.service;

import com.cinema.dto.ReservationDto;
import com.cinema.model.Reservation;
import com.cinema.model.ReservedSeat;
import com.cinema.model.User;
import com.cinema.repository.ReservationRepository;
import com.cinema.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class ReservationService {
    @Autowired
    private ReservationRepository reservationRepository;

    @Autowired
    private UserRepository userRepository;

    public List<Reservation> getAllReservations() {
        return reservationRepository.findAll();
    }

    public Optional<Reservation> getReservationById(Long id) {
        return reservationRepository.findById(id);
    }

    public List<Reservation> getUserReservations(Long userId) {
        return reservationRepository.findUserReservationsOrderedByDate(userId);
    }

    public List<Reservation> getReservationsByMovie(String movieId) {
        return reservationRepository.findByMovieId(movieId);
    }

    public List<Reservation> getReservationsBySchedule(Integer scheduleId) {
        return reservationRepository.findByScheduleId(scheduleId);
    }

    public Reservation createReservation(ReservationDto reservationDto) {
        User user = userRepository.findById(reservationDto.getUserId())
                .orElseThrow(() -> new RuntimeException("User not found with id: " + reservationDto.getUserId()));

        Reservation reservation = new Reservation();
        reservation.setUser(user);
        reservation.setScheduleId(reservationDto.getScheduleId());
        reservation.setMovieId(reservationDto.getMovieId());
        reservation.setTotalAmount(reservationDto.getTotalAmount());

        // Crear asientos reservados
        for (Integer seatId : reservationDto.getSeatIds()) {
            ReservedSeat reservedSeat = new ReservedSeat();
            reservedSeat.setReservation(reservation);
            reservedSeat.setSeatId(seatId);
            reservation.getReservedSeats().add(reservedSeat);
        }

        return reservationRepository.save(reservation);
    }

    public Reservation cancelReservation(Long id) {
        Reservation reservation = reservationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Reservation not found with id: " + id));

        if (reservation.getStatus() == Reservation.ReservationStatus.CANCELLED) {
            throw new RuntimeException("Reservation is already cancelled");
        }

        reservation.setStatus(Reservation.ReservationStatus.CANCELLED);
        return reservationRepository.save(reservation);
    }

    public void deleteReservation(Long id) {
        if (!reservationRepository.existsById(id)) {
            throw new RuntimeException("Reservation not found with id: " + id);
        }
        reservationRepository.deleteById(id);
    }
}