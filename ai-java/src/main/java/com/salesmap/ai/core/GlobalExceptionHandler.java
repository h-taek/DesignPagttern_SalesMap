package com.salesmap.ai.core;

import com.salesmap.ai.predictor.NotEnoughDataException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NotEnoughDataException.class)
    public ResponseEntity<Map<String, Object>> handleNoData(NotEnoughDataException e) {
        return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
            .body(Map.of("error", Map.of("code", "NO_SALES_DATA", "message", e.getMessage())));
    }
}
