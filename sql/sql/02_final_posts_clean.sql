-- FINAL layer: `stg_posts` -> `posts_clean`
-- Job: analyst-friendly table with a few derived columns.

DROP TABLE IF EXISTS posts_clean;

CREATE TABLE posts_clean AS
SELECT
    post_id,
    user_id,
    title,
    body,
    LENGTH(title) AS title_length,
    -- word count = number of spaces + 1 (text is already trimmed in staging)
    LENGTH(body) - LENGTH(REPLACE(body, ' ', '')) + 1 AS body_word_count
FROM stg_posts
ORDER BY post_id;
