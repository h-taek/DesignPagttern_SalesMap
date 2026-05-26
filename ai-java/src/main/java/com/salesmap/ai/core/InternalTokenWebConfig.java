package com.salesmap.ai.core;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class InternalTokenWebConfig implements WebMvcConfigurer {

    private final InternalTokenInterceptor interceptor;

    public InternalTokenWebConfig(InternalTokenInterceptor interceptor) {
        this.interceptor = interceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(interceptor).addPathPatterns("/predict/**");
    }
}
