-- SalesMap schema + seed
-- See docs/04-data-model.md for context.

BEGIN;

CREATE TABLE IF NOT EXISTS region (
    region_id    SERIAL PRIMARY KEY,
    region_name  VARCHAR(20) NOT NULL,
    sgg_code     CHAR(5) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS region_dong_map (
    dong_code  CHAR(10) PRIMARY KEY,
    dong_name  VARCHAR(40) NOT NULL,
    region_id  INT NOT NULL REFERENCES region(region_id)
);

CREATE TABLE IF NOT EXISTS sales_record (
    sales_id           BIGSERIAL PRIMARY KEY,
    region_id          INT NOT NULL REFERENCES region(region_id),
    quarter            CHAR(6) NOT NULL,
    industry_category  VARCHAR(10) NOT NULL
        CHECK (industry_category IN ('food','service','retail')),
    total_sales        BIGINT NOT NULL,
    total_count        BIGINT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (region_id, quarter, industry_category)
);

CREATE INDEX IF NOT EXISTS ix_sales_lookup
    ON sales_record (region_id, industry_category, quarter DESC);

CREATE TABLE IF NOT EXISTS prediction_record (
    prediction_id      BIGSERIAL PRIMARY KEY,
    region_id          INT NOT NULL REFERENCES region(region_id),
    industry_category  VARCHAR(10) NOT NULL
        CHECK (industry_category IN ('food','service','retail')),
    target_quarter     CHAR(6) NOT NULL,
    predicted_sales    BIGINT NOT NULL,
    previous_sales     BIGINT,
    model_slope        DOUBLE PRECISION,
    model_intercept    DOUBLE PRECISION,
    samples_used       INT,
    generated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_prediction_lookup
    ON prediction_record (region_id, industry_category, target_quarter DESC, generated_at DESC);

-- Seed: 서울 25 자치구 (행정안전부 시군구 코드)
INSERT INTO region (region_name, sgg_code) VALUES
    ('종로구','11110'), ('중구','11140'), ('용산구','11170'),
    ('성동구','11200'), ('광진구','11215'), ('동대문구','11230'),
    ('중랑구','11260'), ('성북구','11290'), ('강북구','11305'),
    ('도봉구','11320'), ('노원구','11350'), ('은평구','11380'),
    ('서대문구','11410'), ('마포구','11440'), ('양천구','11470'),
    ('강서구','11500'), ('구로구','11530'), ('금천구','11545'),
    ('영등포구','11560'), ('동작구','11590'), ('관악구','11620'),
    ('서초구','11650'), ('강남구','11680'), ('송파구','11710'),
    ('강동구','11740')
ON CONFLICT (sgg_code) DO NOTHING;

COMMIT;
