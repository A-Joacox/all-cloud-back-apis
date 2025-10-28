package com.cinema.controller;

import com.cinema.dto.ReservationDto;
import com.cinema.dto.ReservationResponseDto;
import com.cinema.model.Reservation;
import com.cinema.service.ReservationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.List;
import java.util.Optional;
import org.springframework.web.bind.annotation.RequestParam;

@RestController
@RequestMapping("/api/reservations")
@CrossOrigin(origins = "*")
@Tag(name = "Reservations", description = "Reservation management operations")
public class ReservationController {
    @Autowired
    private ReservationService reservationService;

    @GetMapping
    public ResponseEntity<?> getAllReservations(
            @RequestParam(required = false, defaultValue = "1000") Integer limit,
            @RequestParam(required = false, defaultValue = "0") Integer offset) {
        try {
            List<Reservation> reservations = reservationService.getAllReservations();
            
            // Apply limit and offset
            int start = Math.min(offset, reservations.size());
            int end = Math.min(offset + limit, reservations.size());
            List<Reservation> paginatedReservations = reservations.subList(start, end);
            
            // Convertir a DTOs
            List<ReservationResponseDto> responseDtos = reservationService.convertToDtoList(paginatedReservations);
            
            return ResponseEntity.ok().body(new ApiResponse(true, responseDtos, null));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(new ApiResponse(false, null, e.getMessage()));
        }
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getReservationById(@PathVariable Long id) {
        try {
            Optional<Reservation> reservation = reservationService.getReservationById(id);
            if (reservation.isPresent()) {
                ReservationResponseDto responseDto = reservationService.convertToDto(reservation.get());
                return ResponseEntity.ok().body(new ApiResponse(true, responseDto, null));
            } else {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(new ApiResponse(false, null, "Reservation not found"));
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(new ApiResponse(false, null, e.getMessage()));
        }
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<?> getUserReservations(@PathVariable Long userId) {
        try {
            List<Reservation> reservations = reservationService.getUserReservations(userId);
            List<ReservationResponseDto> responseDtos = reservationService.convertToDtoList(reservations);
            return ResponseEntity.ok().body(new ApiResponse(true, responseDtos, null));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(new ApiResponse(false, null, e.getMessage()));
        }
    }

    @GetMapping("/movie/{movieId}")
    public ResponseEntity<?> getReservationsByMovie(@PathVariable String movieId) {
        try {
            List<Reservation> reservations = reservationService.getReservationsByMovie(movieId);
            List<ReservationResponseDto> responseDtos = reservationService.convertToDtoList(reservations);
            return ResponseEntity.ok().body(new ApiResponse(true, responseDtos, null));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(new ApiResponse(false, null, e.getMessage()));
        }
    }

    @PostMapping
    public ResponseEntity<?> createReservation(@Valid @RequestBody ReservationDto reservationDto) {
        try {
            Reservation reservation = reservationService.createReservation(reservationDto);
            ReservationResponseDto responseDto = reservationService.convertToDto(reservation);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(new ApiResponse(true, responseDto, null));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(new ApiResponse(false, null, e.getMessage()));
        }
    }

    @PutMapping("/{id}/cancel")
    public ResponseEntity<?> cancelReservation(@PathVariable Long id) {
        try {
            Reservation reservation = reservationService.cancelReservation(id);
            ReservationResponseDto responseDto = reservationService.convertToDto(reservation);
            return ResponseEntity.ok().body(new ApiResponse(true, responseDto, null));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(new ApiResponse(false, null, e.getMessage()));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteReservation(@PathVariable Long id) {
        try {
            reservationService.deleteReservation(id);
            return ResponseEntity.ok().body(new ApiResponse(true, "Reservation deleted successfully", null));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
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