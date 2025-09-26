package com.cinema.model;

import jakarta.persistence.*;

@Entity
@Table(name = "reserved_seats")
public class ReservedSeat {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "reservation_id", nullable = false)
    private Reservation reservation;

    @Column(name = "seat_id")
    private Integer seatId; // Referencia a MySQL

    // Constructors
    public ReservedSeat() {}

    public ReservedSeat(Reservation reservation, Integer seatId) {
        this.reservation = reservation;
        this.seatId = seatId;
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Reservation getReservation() {
        return reservation;
    }

    public void setReservation(Reservation reservation) {
        this.reservation = reservation;
    }

    public Integer getSeatId() {
        return seatId;
    }

    public void setSeatId(Integer seatId) {
        this.seatId = seatId;
    }
}