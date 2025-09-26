package com.cinema.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import java.math.BigDecimal;
import java.util.List;

public class ReservationDto {
    @NotNull
    private Long userId;

    @NotNull
    private Integer scheduleId;

    @NotNull
    private String movieId;

    @NotNull
    @Positive
    private BigDecimal totalAmount;

    @NotNull
    private List<Integer> seatIds;

    // Constructors
    public ReservationDto() {}

    public ReservationDto(Long userId, Integer scheduleId, String movieId, BigDecimal totalAmount, List<Integer> seatIds) {
        this.userId = userId;
        this.scheduleId = scheduleId;
        this.movieId = movieId;
        this.totalAmount = totalAmount;
        this.seatIds = seatIds;
    }

    // Getters and Setters
    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
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

    public List<Integer> getSeatIds() {
        return seatIds;
    }

    public void setSeatIds(List<Integer> seatIds) {
        this.seatIds = seatIds;
    }
}