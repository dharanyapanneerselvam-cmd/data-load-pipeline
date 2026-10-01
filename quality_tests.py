"""Data quality tests.

Each test is a SQL query that returns the BAD rows.
  - 0 rows returned  -> test passes
  - 1+ rows returned -> test FAILS and the whole pipeline run fails

The tests run on the build_* tables BEFORE they are published.
"""

TESTS = {
    "fact_not_empty": """
        SELECT 'fact_posts is empty' AS problem
        WHERE (SELECT COUNT(*) FROM build_fact_posts) = 0
    """,
    "fact_row_count_matches_source": """
        SELECT 'row count differs from posts_clean' AS problem
        WHERE (SELECT COUNT(*) FROM build_fact_posts) <> (SELECT COUNT(*) FROM posts_clean)
    """,
    "fact_no_nulls": """
        SELECT * FROM build_fact_posts
        WHERE post_id IS NULL OR user_key IS NULL OR length_bucket_key IS NULL
           OR title_length IS NULL OR body_word_count IS NULL
    """,
    "fact_post_id_unique": """
        SELECT post_id, COUNT(*) AS n FROM build_fact_posts
        GROUP BY post_id HAVING COUNT(*) > 1
    """,
    "dim_users_user_id_unique": """
        SELECT user_id, COUNT(*) AS n FROM build_dim_users
        GROUP BY user_id HAVING COUNT(*) > 1
    """,
    "fact_user_key_exists_in_dim": """
        SELECT f.* FROM build_fact_posts f
        LEFT JOIN build_dim_users d ON d.user_key = f.user_key
        WHERE f.user_key IS NOT NULL AND d.user_key IS NULL
    """,
    "fact_bucket_key_exists_in_dim": """
        SELECT f.* FROM build_fact_posts f
        LEFT JOIN build_dim_length_bucket d ON d.length_bucket_key = f.length_bucket_key
        WHERE f.length_bucket_key IS NOT NULL AND d.length_bucket_key IS NULL
    """,
    "fact_valid_values": """
        SELECT * FROM build_fact_posts
        WHERE title_length <= 0 OR body_word_count <= 0
    """,
}
