package com.cinema.service;

import com.cinema.dto.ReservationDto;
import com.cinema.dto.ReservationResponseDto;
import com.cinema.dto.UserResponseDto;
import com.cinema.dto.ReservedSeatResponseDto;
import com.cinema.dto.PaymentResponseDto;
import com.cinema.model.Reservation;
import com.cinema.model.ReservedSeat;
import com.cinema.model.User;
import com.cinema.model.Payment;
import com.cinema.repository.ReservationRepository;
import com.cinema.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@Transactional
public class ReservationService {
    @Autowired
    private ReservationRepository reservationRepository;

    @Autowired
    private UserRepository userRepository;

    public List<Reservation> getAllReservations() {
        return reservationRepository.findAllWithPaymentsAndSeats();
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

    // ========== Métodos de conversión Entity -> DTO ==========

    /**
     * Convierte una entidad Reservation a ReservationResponseDto
     */
    public ReservationResponseDto convertToDto(Reservation reservation) {
        if (reservation == null) {
            return null;
        }

        ReservationResponseDto dto = new ReservationResponseDto();
        dto.setId(reservation.getId());
        dto.setScheduleId(reservation.getScheduleId());
        dto.setMovieId(reservation.getMovieId());
        dto.setTotalAmount(reservation.getTotalAmount());
        dto.setStatus(reservation.getStatus() != null ? reservation.getStatus().toString() : null);
        dto.setReservationDate(reservation.getReservationDate());

        // Convertir User
        if (reservation.getUser() != null) {
            dto.setUser(convertUserToDto(reservation.getUser()));
        }

        // Convertir ReservedSeats
        if (reservation.getReservedSeats() != null) {
            dto.setReservedSeats(
                reservation.getReservedSeats().stream()
                    .map(this::convertReservedSeatToDto)
                    .collect(Collectors.toList())
            );
        }

        // Convertir Payment
        if (reservation.getPayment() != null) {
            dto.setPayment(convertPaymentToDto(reservation.getPayment()));
        }

        return dto;
    }

    /**
     * Convierte una entidad User a UserResponseDto
     */
    private UserResponseDto convertUserToDto(User user) {
        if (user == null) {
            return null;
        }
        return new UserResponseDto(
            user.getId(),
            user.getEmail(),
            user.getName(),
            user.getPhone()
        );
    }

    /**
     * Convierte una entidad ReservedSeat a ReservedSeatResponseDto
     */
    private ReservedSeatResponseDto convertReservedSeatToDto(ReservedSeat seat) {
        if (seat == null) {
            return null;
        }
        return new ReservedSeatResponseDto(
            seat.getId(),
            seat.getSeatId(),
            null, // rowNumber no existe en el modelo actual
            null  // seatNumber no existe en el modelo actual
        );
    }

    /**
     * Convierte una entidad Payment a PaymentResponseDto
     */
    private PaymentResponseDto convertPaymentToDto(Payment payment) {
        if (payment == null) {
            return null;
        }
        return new PaymentResponseDto(
            payment.getId(),
            payment.getAmount(),
            payment.getPaymentMethod(),
            payment.getPaymentStatus() != null ? payment.getPaymentStatus().toString() : null,
            payment.getPaymentDate()
        );
    }

    /**
     * Convierte una lista de Reservations a lista de DTOs
     */
    public List<ReservationResponseDto> convertToDtoList(List<Reservation> reservations) {
        if (reservations == null) {
            return null;
        }
        return reservations.stream()
            .map(this::convertToDto)
            .collect(Collectors.toList());
    }
}