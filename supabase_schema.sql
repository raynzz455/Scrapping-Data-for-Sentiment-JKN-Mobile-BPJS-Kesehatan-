-- ═══════════════════════════════════════════════════════════
--  JKN Sentiment — Supabase Schema
--  Jalankan file ini di: Supabase Dashboard → SQL Editor
-- ═══════════════════════════════════════════════════════════

-- Tabel utama ulasan
CREATE TABLE IF NOT EXISTS reviews (
  id             bigserial         PRIMARY KEY,
  scraped_at     timestamptz       NOT NULL DEFAULT now(),
  user_name      text,
  content        text,
  score          smallint          CHECK (score BETWEEN 1 AND 5),
  thumbs_up      integer           DEFAULT 0,
  review_date    date,
  app_version    text,
  sentiment      text              CHECK (sentiment IN ('positif','netral','negatif')),
  sentiment_bin  text              CHECK (sentiment_bin IN ('positif','negatif/netral')),
  reply_content  text,
  reply_date     date
);

-- Unique constraint untuk upsert (hindari duplikat)
CREATE UNIQUE INDEX IF NOT EXISTS idx_reviews_unique
  ON reviews (user_name, review_date)
  WHERE user_name IS NOT NULL AND review_date IS NOT NULL;

-- Index untuk query umum
CREATE INDEX IF NOT EXISTS idx_sentiment    ON reviews (sentiment);
CREATE INDEX IF NOT EXISTS idx_review_date  ON reviews (review_date DESC);
CREATE INDEX IF NOT EXISTS idx_score        ON reviews (score);
CREATE INDEX IF NOT EXISTS idx_scraped_at   ON reviews (scraped_at DESC);

-- Row Level Security (buka read untuk anon, write untuk authenticated)
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY "allow_read" ON reviews
  FOR SELECT USING (true);

CREATE POLICY "allow_insert" ON reviews
  FOR INSERT WITH CHECK (true);

CREATE POLICY "allow_upsert" ON reviews
  FOR UPDATE USING (true);

-- View: ringkasan sentimen
CREATE OR REPLACE VIEW sentiment_summary AS
SELECT
  sentiment,
  COUNT(*)                             AS jumlah,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS persen,
  ROUND(AVG(score), 2)                 AS avg_rating
FROM reviews
WHERE sentiment IS NOT NULL
GROUP BY sentiment
ORDER BY jumlah DESC;

-- View: tren bulanan
CREATE OR REPLACE VIEW monthly_trend AS
SELECT
  TO_CHAR(review_date, 'YYYY-MM') AS bulan,
  sentiment,
  COUNT(*) AS jumlah
FROM reviews
WHERE sentiment IS NOT NULL
  AND review_date IS NOT NULL
GROUP BY bulan, sentiment
ORDER BY bulan, sentiment;
