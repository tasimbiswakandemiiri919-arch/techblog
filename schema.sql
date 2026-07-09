CREATE DATABASE IF NOT EXISTS techblog;
USE techblog;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(10) DEFAULT '#63b3ed'
);

CREATE TABLE IF NOT EXISTS posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    excerpt TEXT NOT NULL,
    content LONGTEXT NOT NULL,
    category_id INT,
    author_id INT NOT NULL,
    status ENUM('draft','published') DEFAULT 'draft',
    views INT DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    CONSTRAINT fk_post_cat FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    CONSTRAINT fk_post_author FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    author_name VARCHAR(100) NOT NULL,
    author_email VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    CONSTRAINT fk_comment_post FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);

-- Seed categories
INSERT INTO categories (name, slug, color) VALUES
('Python', 'python', '#63b3ed'),
('Java', 'java', '#f6ad55'),
('Web Development', 'web-dev', '#68d391'),
('Databases', 'databases', '#fc8181'),
('Cybersecurity', 'cybersecurity', '#b794f4'),
('Algorithms', 'algorithms', '#76e4f7');
