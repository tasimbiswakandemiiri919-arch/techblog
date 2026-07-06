-- ============================================================
-- TechBlog Migration v2
-- Adds: author follows, comment ownership (edit/delete),
--       post scheduling, profile customization
-- Run this AFTER schema.sql on your existing 'techblog' database
-- ============================================================

USE techblog;

-- 1. Profile customization -------------------------------------------------
ALTER TABLE users
    ADD COLUMN avatar_url VARCHAR(255) DEFAULT NULL AFTER bio,
    ADD COLUMN social_links VARCHAR(500) DEFAULT NULL AFTER avatar_url;

-- 2. Author follows ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS follows (
    follower_id INT NOT NULL,
    author_id   INT NOT NULL,
    created_at  DATETIME NOT NULL,
    PRIMARY KEY (follower_id, author_id),
    CONSTRAINT fk_follow_follower FOREIGN KEY (follower_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_follow_author FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT chk_no_self_follow CHECK (follower_id <> author_id)
);

-- 3. Comment ownership (enables edit/delete for logged-in users) ------------
ALTER TABLE comments
    ADD COLUMN user_id INT DEFAULT NULL AFTER post_id,
    ADD COLUMN updated_at DATETIME DEFAULT NULL AFTER created_at,
    ADD CONSTRAINT fk_comment_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL;

-- 4. Post scheduling ----------------------------------------------------------
ALTER TABLE posts
    MODIFY COLUMN status ENUM('draft','scheduled','published') DEFAULT 'draft',
    ADD COLUMN scheduled_at DATETIME DEFAULT NULL AFTER status;

-- Helpful index for search filters (category/author/date already indexed via FKs,
-- this speeds up ORDER BY created_at + LIKE search combos)
CREATE INDEX idx_posts_created ON posts (created_at);
CREATE INDEX idx_posts_status_scheduled ON posts (status, scheduled_at);
