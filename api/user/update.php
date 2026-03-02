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

$fields = ['full_name', 'age', 'gender', 'height', 'weight', 'fitness_goal', 'activity_level'];
$updates = [];
$errors = [];

foreach ($fields as $field) {
    if (array_key_exists($field, $data)) {
        $value = $data[$field];
        
        // 验证每个字段
        switch ($field) {
            case 'full_name':
                $value = trim($value);
                if (strlen($value) > 100) {
                    $errors[] = 'Full name must be less than 100 characters';
                } elseif ($value !== '') {
                    $updates[$field] = $value;
                }
                break;
                
            case 'age':
                $age = (int) $value;
                if ($age < 10 || $age > 120) {
                    $errors[] = 'Age must be between 10 and 120';
                } else {
                    $updates[$field] = $age;
                }
                break;
                
            case 'gender':
                $validGenders = ['male', 'female', 'other'];
                if (!in_array($value, $validGenders)) {
                    $errors[] = 'Gender must be: male, female, or other';
                } else {
                    $updates[$field] = $value;
                }
                break;
                
            case 'height':
                $height = (float) $value;
                if ($height < 100 || $height > 250) {
                    $errors[] = 'Height must be between 100 and 250 cm';
                } else {
                    $updates[$field] = $height;
                }
                break;
                
            case 'weight':
                $weight = (float) $value;
                if ($weight < 30 || $weight > 300) {
                    $errors[] = 'Weight must be between 30 and 300 kg';
                } else {
                    $updates[$field] = $weight;
                }
                break;
                
            case 'fitness_goal':
                $validGoals = ['muscle_gain', 'fat_loss', 'maintenance', 'endurance'];
                if (!in_array($value, $validGoals)) {
                    $errors[] = 'Fitness goal must be: muscle_gain, fat_loss, maintenance, or endurance';
                } else {
                    $updates[$field] = $value;
                }
                break;
                
            case 'activity_level':
                $validLevels = ['sedentary', 'light', 'moderate', 'active', 'very_active'];
                if (!in_array($value, $validLevels)) {
                    $errors[] = 'Activity level must be: sedentary, light, moderate, active, or very_active';
                } else {
                    $updates[$field] = $value;
                }
                break;
        }
    }
}

if (!empty($errors)) {
    json_response(['error' => 'Validation failed', 'details' => $errors], 400);
}

if (!$updates) {
    json_response(['error' => 'No valid fields to update'], 400);
}

try {
    $pdo = Database::getConnection();
    
    // 使用参数化查询防止SQL注入
    $setParts = [];
    $params = [':id' => $userId];
    foreach ($updates as $key => $value) {
        // 确保字段名是白名单中的
        if (in_array($key, $fields)) {
            $setParts[] = "`$key` = :$key";
            $params[":$key"] = $value;
        }
    }
    
    if (empty($setParts)) {
        json_response(['error' => 'No valid fields to update'], 400);
    }
    
    $sql = 'UPDATE users SET ' . implode(', ', $setParts) . ' WHERE id = :id';
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);

    $userStmt = $pdo->prepare('SELECT id, username, email, full_name, age, gender, height, weight, fitness_goal, activity_level, avatar_level, total_workouts, streak_days, total_calories_burned, achievements FROM users WHERE id = :id');
    $userStmt->execute([':id' => $userId]);
    $user = $userStmt->fetch();

    json_response($user);
} catch (Exception $e) {
    json_response(['error' => 'Failed to update profile', 'details' => $e->getMessage()], 500);
}


