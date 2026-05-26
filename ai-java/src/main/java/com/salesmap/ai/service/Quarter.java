package com.salesmap.ai.service;

/** 분기 코드(YYYYQn) ↔ 정수 인덱스. 인덱스 = year * 4 + (n - 1). */
public final class Quarter {

    private Quarter() {}

    public static int toIndex(String q) {
        if (q.length() != 6 || q.charAt(4) != 'Q' || "1234".indexOf(q.charAt(5)) < 0) {
            throw new IllegalArgumentException("invalid quarter: " + q);
        }
        int year = Integer.parseInt(q.substring(0, 4));
        int n = Character.digit(q.charAt(5), 10);
        return year * 4 + (n - 1);
    }

    public static String fromIndex(int idx) {
        int year = Math.floorDiv(idx, 4);
        int rem = Math.floorMod(idx, 4);
        return String.format("%04dQ%d", year, rem + 1);
    }

    public static String nextQuarter(String q) {
        return fromIndex(toIndex(q) + 1);
    }
}
