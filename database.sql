
CREATE DATABASE IF NOT EXISTS cloudnautic_db;

USE cloudnautic_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS login_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

SHOW TABLES;
DESCRIBE users;
DESCRIBE login_history;

CREATE DATABASE IF NOT EXISTS cloudnautic_db;
CREATE USER IF NOT EXISTS 'atul'@'localhost' IDENTIFIED BY 'choose-a-password';
ALTER USER 'atul'@'localhost' IDENTIFIED BY 'choose-a-password';
GRANT ALL PRIVILEGES ON cloudnautic_db.* TO 'atul'@'localhost';
