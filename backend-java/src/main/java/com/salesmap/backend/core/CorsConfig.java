package com.salesmap.backend.core;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
@EnableConfigurationProperties(Settings.class)
public class CorsConfig implements WebMvcConfigurer {
    private final Settings settings;

    public CorsConfig(Settings settings) {
        this.settings = settings;
    }

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins(settings.getCorsOriginList().toArray(new String[0]))
                .allowedMethods("*")
                .allowedHeaders("*");
    }
}
