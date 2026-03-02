<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';
require_once __DIR__ . '/../../includes/auth_check.php';

header('Content-Type: application/json');

$userId = require_login();
$date = $_GET['date'] ?? date('Y-m-d');

try {
    $pdo = Database::getConnection();

    // 具体记录
    $stmt = $pdo->prepare('
        SELECT meal_type, food_name, calories, protein, carbs, fats, log_date, created_at
        FROM nutrition_logs
        WHERE user_id = :user_id AND log_date = :log_date
        ORDER BY created_at DESC
    ');
    $stmt->execute([
        ':user_id' => $userId,
        ':log_date' => $date,
    ]);
    $items = $stmt->fetchAll() ?: [];

    // 汇总
    $totalsStmt = $pdo->prepare('
        SELECT 
            COALESCE(SUM(calories), 0) AS calories,
            COALESCE(SUM(protein), 0)  AS protein,
            COALESCE(SUM(carbs), 0)    AS carbs,
            COALESCE(SUM(fats), 0)     AS fats
        FROM nutrition_logs
        WHERE user_id = :user_id AND log_date = :log_date
    ');
    $totalsStmt->execute([
        ':user_id' => $userId,
        ':log_date' => $date,
    ]);
    $totals = $totalsStmt->fetch() ?: ['calories' => 0, 'protein' => 0, 'carbs' => 0, 'fats' => 0];

    echo json_encode([
        'date' => $date,
        'items' => $items,
        'totals' => [
            'calories' => (int) $totals['calories'],
            'protein' => (float) $totals['protein'],
            'carbs' => (float) $totals['carbs'],
            'fats' => (float) $totals['fats'],
        ],
    ]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to load today nutrition', 'details' => $e->getMessage()]);
}


