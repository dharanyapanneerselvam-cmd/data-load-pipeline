-- DIMENSION: one row per user.
-- Built as build_dim_users first; only renamed to dim_users if all quality tests pass.

DROP TABLE IF EXISTS build_dim_users;

CREATE TABLE build_dim_users AS
SELECT
    ROW_NUMBER() OVER (ORDER BY user_id) AS user_key,   -- surrogate key
    user_id,
    'User ' || user_id                   AS user_label
FROM (SELECT DISTINCT user_id FROM posts_clean WHERE user_id IS NOT NULL);
