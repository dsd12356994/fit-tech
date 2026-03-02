<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';
require_once __DIR__ . '/../../includes/auth_check.php';

header('Content-Type: application/json');

$userId = require_login();

try {
    $pdo = Database::getConnection();
    $stmt = $pdo->prepare('SELECT age, gender, height, weight, fitness_goal, activity_level FROM users WHERE id = :id');
    $stmt->execute([':id' => $userId]);
    $user = $stmt->fetch();

    if (!$user) {
        http_response_code(404);
        echo json_encode(['error' => 'User not found']);
        exit;
    }

    $weight = (float) ($user['weight'] ?? 70);
    $height = (float) ($user['height'] ?? 170);
    $age = (int) ($user['age'] ?? 25);
    $gender = $user['gender'] ?? 'male';
    $goal = $user['fitness_goal'] ?? 'maintenance';
    $activity = $user['activity_level'] ?? 'moderate';

    // BMR: Mifflin-St Jeor
    if ($gender === 'female') {
        $bmr = 10 * $weight + 6.25 * $height - 5 * $age - 161;
    } else {
        $bmr = 10 * $weight + 6.25 * $height - 5 * $age + 5;
    }

    // 活动系数
    $activityFactors = [
        'sedentary' => 1.2,
        'light' => 1.375,
        'moderate' => 1.55,
        'active' => 1.725,
        'very_active' => 1.9,
    ];
    $factor = $activityFactors[$activity] ?? 1.55;
    $maintenanceCalories = $bmr * $factor;

    // 依据目标调整
    if ($goal === 'muscle_gain') {
        $targetCalories = $maintenanceCalories + 500;
        $protein = $weight * 2.0;
    } elseif ($goal === 'fat_loss') {
        $targetCalories = $maintenanceCalories - 500;
        $protein = $weight * 2.0;
    } elseif ($goal === 'endurance') {
        $targetCalories = $maintenanceCalories + 200;
        $protein = $weight * 1.6;
    } else {
        $targetCalories = $maintenanceCalories;
        $protein = $weight * 1.6;
    }

    $targetCalories = max(1200, round($targetCalories));
    $protein = round($protein);
    $fats = round((0.25 * $targetCalories) / 9);
    $carbs = round(($targetCalories - $protein * 4 - $fats * 9) / 4);

    $meals = [
        [
            'meal_type' => 'breakfast',
            'description' => 'Oatmeal with Greek yogurt and berries',
            'calories' => (int) round($targetCalories * 0.25),
        ],
        [
            'meal_type' => 'lunch',
            'description' => 'Chicken breast, rice and mixed vegetables',
            'calories' => (int) round($targetCalories * 0.3),
        ],
        [
            'meal_type' => 'dinner',
            'description' => 'Salmon, potatoes and salad',
            'calories' => (int) round($targetCalories * 0.3),
        ],
        [
            'meal_type' => 'snack',
            'description' => 'Nuts and a piece of fruit',
            'calories' => (int) round($targetCalories * 0.15),
        ],
    ];

    echo json_encode([
        'calories' => $targetCalories,
        'protein' => $protein,
        'carbs' => $carbs,
        'fats' => $fats,
        'meals' => $meals,
    ]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to generate plan', 'details' => $e->getMessage()]);
}


