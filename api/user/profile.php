<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';
require_once __DIR__ . '/../../includes/auth_check.php';

header('Content-Type: application/json');

$userId = require_login();

try {
    $pdo = Database::getConnection();
    $stmt = $pdo->prepare('SELECT id, username, email, full_name, age, gender, height, weight, fitness_goal, activity_level, avatar_level, total_workouts, streak_days, total_calories_burned, achievements FROM users WHERE id = :id');
    $stmt->execute([':id' => $userId]);
    $user = $stmt->fetch();

    if (!$user) {
        http_response_code(404);
        echo json_encode(['error' => 'User not found']);
        exit;
    }

    echo json_encode($user);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to load profile', 'details' => $e->getMessage()]);
}


