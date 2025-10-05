package com.cinema.repository;

import com.cinema.model.Reservation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ReservationRepository extends JpaRepository<Reservation, Long> {
    List<Reservation> findByUserId(Long userId);
    List<Reservation> findByMovieId(String movieId);
    List<Reservation> findByScheduleId(Integer scheduleId);
    
    @Query("SELECT r FROM Reservation r WHERE r.user.id = :userId ORDER BY r.reservationDate DESC")
    List<Reservation> findUserReservationsOrderedByDate(@Param("userId") Long userId);
    
    @Query("SELECT DISTINCT r FROM Reservation r " +
           "LEFT JOIN FETCH r.payment " +
           "LEFT JOIN FETCH r.reservedSeats " +
           "LEFT JOIN FETCH r.user")
    List<Reservation> findAllWithPaymentsAndSeats();
}