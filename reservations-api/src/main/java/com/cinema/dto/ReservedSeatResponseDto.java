package com.cinema.dto;

/**
 * DTO para respuestas de Asiento Reservado (sin referencias circulares)
 */
public class ReservedSeatResponseDto {
    private Long id;
    private Integer seatId;
    private Integer rowNumber;
    private Integer seatNumber;

    // Constructors
    public ReservedSeatResponseDto() {}

    public ReservedSeatResponseDto(Long id, Integer seatId, Integer rowNumber, Integer seatNumber) {
        this.id = id;
        this.seatId = seatId;
        this.rowNumber = rowNumber;
        this.seatNumber = seatNumber;
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getSeatId() {
        return seatId;
    }

    public void setSeatId(Integer seatId) {
        this.seatId = seatId;
    }

    public Integer getRowNumber() {
        return rowNumber;
    }

    public void setRowNumber(Integer rowNumber) {
        this.rowNumber = rowNumber;
    }

    public Integer getSeatNumber() {
        return seatNumber;
    }

    public void setSeatNumber(Integer seatNumber) {
        this.seatNumber = seatNumber;
    }
}
