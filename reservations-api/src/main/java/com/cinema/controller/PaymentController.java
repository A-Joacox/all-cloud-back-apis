package com.cinema.controller;

import com.cinema.dto.PaymentDto;
import com.cinema.model.Payment;
import com.cinema.service.PaymentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.Optional;

@RestController
@RequestMapping("/api/payments")
@CrossOrigin(origins = "*")
public class PaymentController {
    @Autowired
    private PaymentService paymentService;

    @PostMapping
    public ResponseEntity<?> processPayment(@Valid @RequestBody PaymentDto paymentDto) {
        try {
            Payment payment = paymentService.processPayment(paymentDto);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(new ApiResponse(true, payment, null));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(new ApiResponse(false, null, e.getMessage()));
        }
    }

    @GetMapping("/reservation/{reservationId}")
    public ResponseEntity<?> getPaymentByReservationId(@PathVariable Long reservationId) {
        try {
            Optional<Payment> payment = paymentService.getPaymentByReservationId(reservationId);
            if (payment.isPresent()) {
                return ResponseEntity.ok().body(new ApiResponse(true, payment.get(), null));
            } else {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(new ApiResponse(false, null, "Payment not found"));
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(new ApiResponse(false, null, e.getMessage()));
        }
    }

    // Clase interna para respuesta API
    public static class ApiResponse {
        private boolean success;
        private Object data;
        private String error;

        public ApiResponse(boolean success, Object data, String error) {
            this.success = success;
            this.data = data;
            this.error = error;
        }

        // Getters and Setters
        public boolean isSuccess() {
            return success;
        }

        public void setSuccess(boolean success) {
            this.success = success;
        }

        public Object getData() {
            return data;
        }

        public void setData(Object data) {
            this.data = data;
        }

        public String getError() {
            return error;
        }

        public void setError(String error) {
            this.error = error;
        }
    }
}