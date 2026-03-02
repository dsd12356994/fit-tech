-- FitTech 数据库初始化脚本

CREATE DATABASE IF NOT EXISTS fittech_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fittech_db;

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    age INT,
    gender ENUM('male', 'female', 'other'),
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    fitness_goal ENUM('muscle_gain', 'fat_loss', 'maintenance', 'endurance'),
    activity_level ENUM('sedentary', 'light', 'moderate', 'active', 'very_active'),
    avatar_level INT DEFAULT 1,
    total_workouts INT DEFAULT 0,
    streak_days INT DEFAULT 0,
    total_calories_burned INT DEFAULT 0,
    achievements INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS workouts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    workout_type ENUM('strength', 'cardio', 'hiit', 'yoga', 'other'),
    duration_minutes INT NOT NULL,
    intensity ENUM('light', 'moderate', 'hard', 'extreme'),
    calories_burned INT,
    notes TEXT,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_date (user_id, date)
);

CREATE TABLE IF NOT EXISTS nutrition_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    meal_type ENUM('breakfast', 'lunch', 'dinner', 'snack'),
    food_name VARCHAR(100),
    calories INT,
    protein DECIMAL(5,2),
    carbs DECIMAL(5,2),
    fats DECIMAL(5,2),
    log_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category ENUM('supplements', 'equipment', 'apparel', 'accessories'),
    price DECIMAL(10,2) NOT NULL,
    original_price DECIMAL(10,2),
    image_url VARCHAR(255),
    badge ENUM('bestseller', 'new', 'sale', 'none') DEFAULT 'none',
    stock_quantity INT DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cart_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_cart_item (user_id, product_id)
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    achievement_type VARCHAR(50),
    title VARCHAR(100),
    description TEXT,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO products (name, description, category, price, original_price, badge) VALUES
('Protein Powder', 'Premium whey protein isolate for muscle recovery', 'supplements', 39.99, 49.99, 'bestseller'),
('Adjustable Dumbbells', '5-50 lbs adjustable weight set', 'equipment', 129.99, NULL, 'new'),
('Performance T-Shirt', 'Moisture-wicking fabric for intense workouts', 'apparel', 24.99, NULL, 'none'),
('Fitness Tracker', 'Track workouts, heart rate, and sleep', 'accessories', 89.99, 119.99, 'sale');


