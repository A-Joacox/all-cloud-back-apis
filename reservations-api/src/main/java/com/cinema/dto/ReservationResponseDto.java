package com.cinema.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

/**
 * DTO para respuestas de Reserva (sin referencias circulares)
 */
public class ReservationResponseDto {
    private Long id;
    private UserResponseDto user;
    private Integer scheduleId;
    private String movieId;
    private BigDecimal totalAmount;
    private String status;
    private LocalDateTime reservationDate;
    private List<ReservedSeatResponseDto> reservedSeats;
    private PaymentResponseDto payment;

    // Constructors
    public ReservationResponseDto() {}

    public ReservationResponseDto(Long id, UserResponseDto user, Integer scheduleId, 
                                  String movieId, BigDecimal totalAmount, String status, 
                                  LocalDateTime reservationDate, List<ReservedSeatResponseDto> reservedSeats,
                                  PaymentResponseDto payment) {
        this.id = id;
        this.user = user;
        this.scheduleId = scheduleId;
        this.movieId = movieId;
        this.totalAmount = totalAmount;
        this.status = status;
        this.reservationDate = reservationDate;
        this.reservedSeats = reservedSeats;
        this.payment = payment;
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public UserResponseDto getUser() {
        return user;
    }

    public void setUser(UserResponseDto user) {
        this.user = user;
    }

    public Integer getScheduleId() {
        return scheduleId;
    }

    public void setScheduleId(Integer scheduleId) {
        this.scheduleId = scheduleId;
    }

    public String getMovieId() {
        return movieId;
    }

    public void setMovieId(String movieId) {
        this.movieId = movieId;
    }

    public BigDecimal getTotalAmount() {
        return totalAmount;
    }

    public void setTotalAmount(BigDecimal totalAmount) {
        this.totalAmount = totalAmount;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public LocalDateTime getReservationDate() {
        return reservationDate;
    }

    public void setReservationDate(LocalDateTime reservationDate) {
        this.reservationDate = reservationDate;
    }

    public List<ReservedSeatResponseDto> getReservedSeats() {
        return reservedSeats;
    }

    public void setReservedSeats(List<ReservedSeatResponseDto> reservedSeats) {
        this.reservedSeats = reservedSeats;
    }

    public PaymentResponseDto getPayment() {
        return payment;
    }

    public void setPayment(PaymentResponseDto payment) {
        this.payment = payment;
    }
}
