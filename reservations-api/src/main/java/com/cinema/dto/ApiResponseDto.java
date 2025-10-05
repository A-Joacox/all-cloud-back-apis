package com.cinema.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Standard API response wrapper")
public class ApiResponseDto {
    
    @Schema(description = "Indicates if the operation was successful", example = "true")
    private boolean success;
    
    @Schema(description = "Response data payload")
    private Object data;
    
    @Schema(description = "Error message if operation failed", example = "null")
    private String message;
    
    public ApiResponseDto() {}
    
    public ApiResponseDto(boolean success, Object data, String message) {
        this.success = success;
        this.data = data;
        this.message = message;
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
    
    public String getMessage() {
        return message;
    }
    
    public void setMessage(String message) {
        this.message = message;
    }
}