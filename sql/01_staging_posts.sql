-- STAGING layer: raw `posts` -> `stg_posts`
-- Job: type casting, trimming, deduplication. No business logic here.

DROP TABLE IF EXISTS stg_posts;

CREATE TABLE stg_posts AS
WITH casted AS (
    SELECT
        CAST(id      AS INTEGER) AS post_id,
        CAST(user_id AS INTEGER) AS user_id,
        TRIM(title)              AS title,
        -- API bodies have newlines; flatten them so analysts get clean text
        TRIM(REPLACE(body, CHAR(10), ' ')) AS body
    FROM posts
    WHERE id IS NOT NULL
),
ranked AS (
    SELECT
        *,
        -- same post_id more than once? keep only one row
        ROW_NUMBER() OVER (PARTITION BY post_id ORDER BY post_id) AS rn
    FROM casted
)
SELECT post_id, user_id, title, body
FROM ranked
WHERE rn = 1;
