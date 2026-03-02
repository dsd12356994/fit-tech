<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';
require_once __DIR__ . '/../../includes/auth_check.php';

header('Content-Type: application/json');

$userId = require_login();
$limit = isset($_GET['limit']) ? max(1, (int) $_GET['limit']) : 10;

try {
    $pdo = Database::getConnection();
    $stmt = $pdo->prepare('
        SELECT workout_type, duration_minutes, intensity, calories_burned, notes, date, created_at
        FROM workouts
        WHERE user_id = :user_id
        ORDER BY date DESC, created_at DESC
        LIMIT :limit
    ');
    $stmt->bindValue(':user_id', $userId, PDO::PARAM_INT);
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->execute();

    $rows = $stmt->fetchAll() ?: [];

    echo json_encode(['items' => $rows]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to load workouts', 'details' => $e->getMessage()]);
}


