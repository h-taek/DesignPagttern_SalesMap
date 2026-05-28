package com.salesmap.backend.service.ingest;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.salesmap.backend.core.Settings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

/** 서울 열린데이터 광장 OA-15572 호출 (JSON). */
@Component
public class OpenApiClient {

    private static final Logger log = LoggerFactory.getLogger(OpenApiClient.class);
    private static final int PAGE = 1000;
    private static final String SERVICE_NAME = "VwsmTrdarSelngQq";

    private final Settings settings;
    private final ObjectMapper objectMapper;
    private final WebClient client;

    public OpenApiClient(Settings settings, ObjectMapper objectMapper) {
        this.settings = settings;
        this.objectMapper = objectMapper;
        // OA-15572 1페이지(1000행)가 기본 256KB 한도를 초과하므로 in-memory 버퍼를 16MB로 확대
        this.client = WebClient.builder()
            .codecs(c -> c.defaultCodecs().maxInMemorySize(16 * 1024 * 1024))
            .build();
    }

    /** quarter는 '20244' 형식. null이면 전체. */
    public Iterator<Map<String, Object>> fetchQuarter(String yearQuarter) {
        String key = settings.getOpenApiKey();
        if (key == null || key.isEmpty()) {
            log.error("OPEN_API_KEY_MISSING");
            throw new RuntimeException("OPEN_API_KEY is empty");
        }
        String base = settings.getOpenApiBase().replaceAll("/+$", "");
        String maskedKey = key.length() > 4 ? key.substring(0, 4) + "****" : "****";

        return new Iterator<>() {
            int start = 1;
            Iterator<Map<String, Object>> current = List.<Map<String, Object>>of().iterator();
            boolean done = false;

            @Override
            public boolean hasNext() {
                while (!current.hasNext() && !done) {
                    List<Map<String, Object>> rows = fetchPage(start);
                    if (rows.isEmpty()) { done = true; return false; }
                    current = rows.iterator();
                    if (rows.size() < PAGE) done = true;
                    start += PAGE;
                }
                return current.hasNext();
            }

            @Override
            public Map<String, Object> next() {
                return current.next();
            }

            private List<Map<String, Object>> fetchPage(int s) {
                int end = s + PAGE - 1;
                StringBuilder url = new StringBuilder(base);
                url.append('/').append(key).append("/json/").append(SERVICE_NAME)
                   .append('/').append(s).append('/').append(end);
                if (yearQuarter != null) url.append('/').append(yearQuarter);

                log.info("fetching_external_api url={}/{}/json/{}/... quarter={}",
                    base, maskedKey, SERVICE_NAME, yearQuarter);

                try {
                    String body = client.get().uri(url.toString())
                        .retrieve().bodyToMono(String.class)
                        .block(Duration.ofSeconds(30));
                    if (body == null) return List.of();
                    Map<String, Object> root = objectMapper.readValue(body,
                        new TypeReference<Map<String, Object>>() {});
                    Object svc = root.get(SERVICE_NAME);
                    if (!(svc instanceof Map<?, ?> svcMap)) return List.of();
                    Object rowsObj = svcMap.get("row");
                    if (!(rowsObj instanceof List<?> rowsList)) return List.of();
                    List<Map<String, Object>> out = new ArrayList<>(rowsList.size());
                    for (Object o : rowsList) {
                        if (o instanceof Map<?, ?> mm) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> typed = (Map<String, Object>) mm;
                            out.add(typed);
                        }
                    }
                    log.info("fetched_rows count={} start={} end={}", out.size(), s, end);
                    return out;
                } catch (Exception e) {
                    log.error("external_api_error", e);
                    throw new RuntimeException(e);
                }
            }
        };
    }
}
