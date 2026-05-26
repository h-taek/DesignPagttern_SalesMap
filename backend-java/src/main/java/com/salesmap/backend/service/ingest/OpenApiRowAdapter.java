package com.salesmap.backend.service.ingest;

import com.salesmap.backend.dto.IndustryCategory;

import java.util.Map;

/** OA-15572 원본 행 → NormalizedRow. 실패는 AdaptResult.fail로 반환. */
public class OpenApiRowAdapter {

    private static final String[] COL_QUARTER = {"STDR_YYQU_CD", "stdr_yyqu_cd", "quarter_raw"};
    private static final String[] COL_INDUSTRY = {"SVC_INDUTY_CD", "svc_induty_cd"};
    private static final String[] COL_SALES = {"THSMON_SELNG_AMT", "thsmon_selng_amt", "total_sales"};
    private static final String[] COL_COUNT = {"THSMON_SELNG_CO", "thsmon_selng_co", "total_count"};
    private static final String[] COL_SGG = {"SGG_CD", "sgg_code"};
    private static final String[] COL_DONG = {"ADSTRD_CD", "adstrd_cd", "dong_code"};
    private static final String[] COL_TRDAR = {"TRDAR_CD", "trdar_cd"};

    private final IndustryMap industry;
    private final RegionResolver region;

    public OpenApiRowAdapter(IndustryMap industry, RegionResolver region) {
        this.industry = industry;
        this.region = region;
    }

    public AdaptResult adapt(Map<String, Object> raw) {
        String quarterRaw = pick(raw, COL_QUARTER);
        String quarter;
        try {
            quarter = parseQuarter(quarterRaw == null ? "" : quarterRaw);
        } catch (AdaptError e) {
            return AdaptResult.fail(e.code + ":" + e.getMessage());
        }

        long sales;
        Long countInt = null;
        try {
            sales = parseAmount(pick(raw, COL_SALES) == null ? "" : pick(raw, COL_SALES));
            String count = pick(raw, COL_COUNT);
            if (count != null) countInt = parseAmount(count);
        } catch (AdaptError e) {
            return AdaptResult.fail(e.code + ":" + e.getMessage());
        }

        if (sales < 0) return AdaptResult.fail("NEGATIVE_SALES:" + sales);
        if (countInt != null && countInt < 0) return AdaptResult.fail("NEGATIVE_COUNT:" + countInt);

        String svcCd = pick(raw, COL_INDUSTRY);
        if (svcCd == null) return AdaptResult.fail("MISSING_INDUSTRY_CODE");
        IndustryCategory ind = industry.get(svcCd);
        if (ind == null) return AdaptResult.fail("UNMAPPED_INDUSTRY:" + svcCd);

        Integer regionId = region.resolve(pick(raw, COL_SGG), pick(raw, COL_DONG), pick(raw, COL_TRDAR));
        if (regionId == null) return AdaptResult.fail("UNMAPPED_REGION");

        return AdaptResult.ok(new NormalizedRow(regionId, quarter, ind, sales, countInt));
    }

    private static String pick(Map<String, Object> raw, String[] keys) {
        for (String k : keys) {
            Object v = raw.get(k);
            if (v == null) continue;
            String s = v.toString().strip();
            if (s.isEmpty()) continue;
            return s;
        }
        return null;
    }

    private static String parseQuarter(String s) {
        s = s.strip();
        if (s.length() == 5 && s.chars().allMatch(Character::isDigit) && "1234".indexOf(s.charAt(4)) >= 0) {
            return s.substring(0, 4) + "Q" + s.charAt(4);
        }
        if (s.length() == 6 && s.substring(0, 4).chars().allMatch(Character::isDigit)
                && s.charAt(4) == 'Q' && "1234".indexOf(s.charAt(5)) >= 0) {
            return s.toUpperCase();
        }
        throw new AdaptError("BAD_QUARTER", "invalid quarter: " + s);
    }

    private static long parseAmount(String s) {
        s = s.replace(",", "").strip();
        if (s.isEmpty() || s.equals("-")) throw new AdaptError("BAD_AMOUNT", "empty amount");
        return (long) Double.parseDouble(s);
    }

    private static class AdaptError extends RuntimeException {
        final String code;
        AdaptError(String code, String msg) { super(msg); this.code = code; }
    }
}
