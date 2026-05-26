package com.salesmap.backend.service.ingest;

import com.salesmap.backend.dto.IndustryCategory;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** OA-15572 서비스 업종 코드 → 대분류(food/service/retail) 매핑. infra/db/industry_map.csv. */
public class IndustryMap {

    private final Map<String, IndustryCategory> map;

    public IndustryMap(Map<String, IndustryCategory> map) {
        this.map = map;
    }

    public IndustryCategory get(String svcIndutyCd) {
        return map.get(svcIndutyCd);
    }

    public static IndustryMap fromCsv(Path path) {
        Map<String, IndustryCategory> m = new HashMap<>();
        try (BufferedReader r = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
            String header = null;
            String line;
            while ((line = r.readLine()) != null) {
                if (line.stripLeading().startsWith("#")) continue;
                if (header == null) { header = line; continue; }
                List<String> cols = splitCsv(header);
                List<String> vals = splitCsv(line);
                int codeIdx = cols.indexOf("svc_induty_cd");
                int catIdx = cols.indexOf("industry_category");
                if (codeIdx < 0 || catIdx < 0 || codeIdx >= vals.size() || catIdx >= vals.size()) continue;
                String code = vals.get(codeIdx).strip();
                String cat = vals.get(catIdx).strip();
                if (code.isEmpty()) continue;
                try {
                    m.put(code, IndustryCategory.valueOf(cat));
                } catch (IllegalArgumentException ignore) {
                    // 비대분류는 스킵
                }
            }
        } catch (IOException e) {
            throw new RuntimeException("failed to read industry map: " + path, e);
        }
        return new IndustryMap(m);
    }

    private static List<String> splitCsv(String line) {
        return List.of(line.split(",", -1));
    }
}
