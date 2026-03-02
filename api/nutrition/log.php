<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';
require_once __DIR__ . '/../../includes/functions.php';
require_once __DIR__ . '/../../includes/auth_check.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['error' => 'Method not allowed'], 405);
}

$userId = require_login();
$data = json_input();

require_fields($data, ['meal_type', 'food_name', 'calories']);

// 验证餐次类型
$validMealTypes = ['breakfast', 'lunch', 'dinner', 'snack'];
$mealType = $data['meal_type'];
if (!in_array($mealType, $validMealTypes)) {
    json_response(['error' => 'Invalid meal type. Must be: breakfast, lunch, dinner, or snack'], 400);
}

// 验证食物名称
$foodName = trim($data['food_name']);
if (empty($foodName)) {
    json_response(['error' => 'Food name cannot be empty'], 400);
}
if (strlen($foodName) > 100) {
    json_response(['error' => 'Food name must be less than 100 characters'], 400);
}

// 验证卡路里
$calories = (int) $data['calories'];
if ($calories < 0 || $calories > 10000) {
    json_response(['error' => 'Calories must be between 0 and 10000'], 400);
}

// 验证营养素（可选）
$protein = isset($data['protein']) ? (float) $data['protein'] : 0;
$carbs = isset($data['carbs']) ? (float) $data['carbs'] : 0;
$fats = isset($data['fats']) ? (float) $data['fats'] : 0;

if ($protein < 0 || $protein > 1000) {
    json_response(['error' => 'Protein must be between 0 and 1000 grams'], 400);
}
if ($carbs < 0 || $carbs > 1000) {
    json_response(['error' => 'Carbs must be between 0 and 1000 grams'], 400);
}
if ($fats < 0 || $fats > 1000) {
    json_response(['error' => 'Fats must be between 0 and 1000 grams'], 400);
}

// 验证日期
$logDate = $data['log_date'] ?? date('Y-m-d');
if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $logDate)) {
    json_response(['error' => 'Invalid date format. Use YYYY-MM-DD'], 400);
}
$dateObj = new DateTime($logDate);
$today = new DateTime();
$minDate = new DateTime('2020-01-01');
if ($dateObj > $today) {
    json_response(['error' => 'Cannot log nutrition for future dates'], 400);
}
if ($dateObj < $minDate) {
    json_response(['error' => 'Date is too far in the past'], 400);
}

try {
    $pdo = Database::getConnection();
    $stmt = $pdo->prepare('
        INSERT INTO nutrition_logs (user_id, meal_type, food_name, calories, protein, carbs, fats, log_date, created_at)
        VALUES (:user_id, :meal_type, :food_name, :calories, :protein, :carbs, :fats, :log_date, NOW())
    ');
    $stmt->execute([
        ':user_id' => $userId,
        ':meal_type' => $mealType,
        ':food_name' => $foodName,
        ':calories' => $calories,
        ':protein' => $protein,
        ':carbs' => $carbs,
        ':fats' => $fats,
        ':log_date' => $logDate,
    ]);

    json_response(['success' => true]);
} catch (Exception $e) {
    json_response(['error' => 'Failed to log nutrition', 'details' => $e->getMessage()], 500);
}


