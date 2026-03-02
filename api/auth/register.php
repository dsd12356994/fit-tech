<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';
require_once __DIR__ . '/../../includes/functions.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['error' => 'Method not allowed'], 405);
}

$data = json_input();

require_fields($data, ['email', 'password', 'full_name']);

$email = trim(strtolower($data['email']));
$password = $data['password'];
$fullName = trim($data['full_name']);

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    json_response(['error' => 'Invalid email format'], 422);
}

if (strlen($password) < 6) {
    json_response(['error' => 'Password must be at least 6 characters'], 422);
}

$age = isset($data['age']) ? (int) $data['age'] : null;
$gender = $data['gender'] ?? null;
$height = isset($data['height']) ? (float) $data['height'] : null;
$weight = isset($data['weight']) ? (float) $data['weight'] : null;
$fitnessGoal = $data['fitness_goal'] ?? null;
$activityLevel = $data['activity_level'] ?? null;

try {
    $pdo = Database::getConnection();

    // 检查邮箱是否已存在
    $stmt = $pdo->prepare('SELECT id FROM users WHERE email = :email LIMIT 1');
    $stmt->execute([':email' => $email]);
    if ($stmt->fetch()) {
        json_response(['error' => 'Email is already registered'], 409);
    }

    $passwordHash = password_hash($password, PASSWORD_DEFAULT);
    $username = explode('@', $email)[0];

    $stmt = $pdo->prepare('
        INSERT INTO users 
        (username, email, password_hash, full_name, age, gender, height, weight, fitness_goal, activity_level, created_at) 
        VALUES (:username, :email, :password_hash, :full_name, :age, :gender, :height, :weight, :fitness_goal, :activity_level, NOW())
    ');

    $stmt->execute([
        ':username' => $username,
        ':email' => $email,
        ':password_hash' => $passwordHash,
        ':full_name' => $fullName,
        ':age' => $age,
        ':gender' => $gender,
        ':height' => $height,
        ':weight' => $weight,
        ':fitness_goal' => $fitnessGoal,
        ':activity_level' => $activityLevel,
    ]);

    $userId = (int) $pdo->lastInsertId();
    $_SESSION['user_id'] = $userId;

    $userStmt = $pdo->prepare('SELECT id, username, email, full_name, age, gender, height, weight, fitness_goal, activity_level, avatar_level, total_workouts, streak_days, total_calories_burned, achievements FROM users WHERE id = :id');
    $userStmt->execute([':id' => $userId]);
    $user = $userStmt->fetch();

    json_response($user);
} catch (Exception $e) {
    json_response(['error' => 'Registration failed', 'details' => $e->getMessage()], 500);
}


