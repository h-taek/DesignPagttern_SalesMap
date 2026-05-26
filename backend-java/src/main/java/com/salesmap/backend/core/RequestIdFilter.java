package com.salesmap.backend.core;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.UUID;

/** Python RequestIdMiddleware + structlog contextvars 동등물. MDC로 로그 컨텍스트 주입. */
@Component
public class RequestIdFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        String requestId = request.getHeader("X-Request-Id");
        if (requestId == null || requestId.isEmpty()) {
            requestId = UUID.randomUUID().toString();
        }
        MDC.put("request_id", requestId);
        String n8nExec = request.getHeader("X-N8n-Execution-Id");
        if (n8nExec != null) MDC.put("n8n_execution_id", n8nExec);
        MDC.put("service", "backend");
        try {
            response.setHeader("X-Request-Id", requestId);
            chain.doFilter(request, response);
        } finally {
            MDC.clear();
        }
    }
}
