<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';
require_once __DIR__ . '/../../includes/auth_check.php';

header('Content-Type: application/json');

$userId = require_login();

try {
    $pdo = Database::getConnection();

    // 从 users 表直接读取累计字段
    $userStmt = $pdo->prepare('
        SELECT total_workouts, streak_days, total_calories_burned, achievements
        FROM users
        WHERE id = :id
    ');
    $userStmt->execute([':id' => $userId]);
    $userStats = $userStmt->fetch() ?: [
        'total_workouts' => 0,
        'streak_days' => 0,
        'total_calories_burned' => 0,
        'achievements' => 0,
    ];

    $response = [
        'total_workouts' => (int) $userStats['total_workouts'],
        'streak_days' => (int) $userStats['streak_days'],
        'total_calories' => (int) $userStats['total_calories_burned'],
        'achievements_count' => (int) $userStats['achievements'],
    ];

    echo json_encode($response);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to load stats', 'details' => $e->getMessage()]);
}


