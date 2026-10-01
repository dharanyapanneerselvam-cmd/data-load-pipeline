-- FACT: one row per post (grain = post).
-- LEFT JOINs on purpose: if a key is missing we get NULL, and the quality tests catch it.

DROP TABLE IF EXISTS build_fact_posts;

CREATE TABLE build_fact_posts AS
SELECT
    p.post_id,
    u.user_key,
    b.length_bucket_key,
    p.title_length,
    p.body_word_count
FROM posts_clean AS p
LEFT JOIN build_dim_users         AS u ON u.user_id = p.user_id
LEFT JOIN build_dim_length_bucket AS b ON p.body_word_count BETWEEN b.min_words AND b.max_words;
