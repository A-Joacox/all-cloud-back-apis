package com.cinema.service;

import com.cinema.dto.PaymentDto;
import com.cinema.model.Payment;
import com.cinema.model.Reservation;
import com.cinema.repository.ReservationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
@Transactional
public class PaymentService {
    @Autowired
    private ReservationRepository reservationRepository;

    public Payment processPayment(PaymentDto paymentDto) {
        Reservation reservation = reservationRepository.findById(paymentDto.getReservationId())
                .orElseThrow(() -> new RuntimeException("Reservation not found with id: " + paymentDto.getReservationId()));

        if (reservation.getPayment() != null) {
            throw new RuntimeException("Payment already exists for this reservation");
        }

        Payment payment = new Payment();
        payment.setReservation(reservation);
        payment.setAmount(paymentDto.getAmount());
        payment.setPaymentMethod(paymentDto.getPaymentMethod());
        payment.setTransactionId(generateTransactionId());

        // Simular procesamiento de pago
        if (processPayment(paymentDto.getPaymentMethod(), paymentDto.getAmount())) {
            payment.setPaymentStatus(Payment.PaymentStatus.COMPLETED);
            reservation.setStatus(Reservation.ReservationStatus.CONFIRMED);
        } else {
            payment.setPaymentStatus(Payment.PaymentStatus.FAILED);
        }

        reservation.setPayment(payment);
        reservationRepository.save(reservation);

        return payment;
    }

    public Optional<Payment> getPaymentByReservationId(Long reservationId) {
        Reservation reservation = reservationRepository.findById(reservationId)
                .orElseThrow(() -> new RuntimeException("Reservation not found with id: " + reservationId));
        return Optional.ofNullable(reservation.getPayment());
    }

    private String generateTransactionId() {
        return "TXN" + System.currentTimeMillis();
    }

    private boolean processPayment(String paymentMethod, java.math.BigDecimal amount) {
        // Simulación de procesamiento de pago
        // En un entorno real, aquí se integraría con un procesador de pagos
        return true; // Simular éxito
    }
}