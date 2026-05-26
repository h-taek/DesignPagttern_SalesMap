package com.salesmap.ai.core;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.util.Map;

@Component
public class InternalTokenInterceptor implements HandlerInterceptor {

    private final Settings settings;
    private final ObjectMapper objectMapper;

    public InternalTokenInterceptor(Settings settings, ObjectMapper objectMapper) {
        this.settings = settings;
        this.objectMapper = objectMapper;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {
        String header = request.getHeader("X-Internal-Token");
        if (header == null || !header.equals(settings.getInternalToken())) {
            response.setStatus(HttpStatus.UNAUTHORIZED.value());
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            response.getWriter().write(objectMapper.writeValueAsString(Map.of(
                "error", Map.of("code", "UNAUTHORIZED", "message", "invalid internal token")
            )));
            return false;
        }
        return true;
    }
}
