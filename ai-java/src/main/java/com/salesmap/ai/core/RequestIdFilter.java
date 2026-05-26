package com.salesmap.ai.core;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.UUID;

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
        MDC.put("service", "ai");
        try {
            response.setHeader("X-Request-Id", requestId);
            chain.doFilter(request, response);
        } finally {
            MDC.clear();
        }
    }
}
