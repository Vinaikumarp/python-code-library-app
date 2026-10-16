CREATE DATABASE digital_library;
USE digital_library;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    author VARCHAR(100)
);

CREATE TABLE borrow_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample books
INSERT INTO books (title, author) VALUES
("Docker Book", "Mustafa"),
("Kubernetes", "Mustafa Shaik"),
("Terraform", "Musta");

GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root';
FLUSH PRIVILEGES;
