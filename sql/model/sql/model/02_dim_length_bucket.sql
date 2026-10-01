-- DIMENSION: post length buckets (small static lookup table).

DROP TABLE IF EXISTS build_dim_length_bucket;

CREATE TABLE build_dim_length_bucket AS
SELECT 1 AS length_bucket_key, 'short'  AS bucket_name, 1  AS min_words, 19   AS max_words
UNION ALL
SELECT 2, 'medium', 20, 29
UNION ALL
SELECT 3, 'long',   30, 9999;
