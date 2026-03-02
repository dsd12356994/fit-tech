<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';
require_once __DIR__ . '/../../includes/functions.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['error' => 'Method not allowed'], 405);
}

$data = json_input();

require_fields($data, ['email', 'password']);

$email = trim(strtolower($data['email']));
$password = $data['password'];

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    json_response(['error' => 'Invalid email or password'], 401);
}

try {
    $pdo = Database::getConnection();
    $stmt = $pdo->prepare('SELECT * FROM users WHERE email = :email LIMIT 1');
    $stmt->execute([':email' => $email]);
    $user = $stmt->fetch();

    if (!$user || !password_verify($password, $user['password_hash'])) {
        json_response(['error' => 'Invalid email or password'], 401);
    }

    $_SESSION['user_id'] = (int) $user['id'];

    $update = $pdo->prepare('UPDATE users SET last_login = NOW() WHERE id = :id');
    $update->execute([':id' => $user['id']]);

    $response = [
        'id' => (int) $user['id'],
        'username' => $user['username'],
        'email' => $user['email'],
        'full_name' => $user['full_name'],
        'age' => $user['age'],
        'gender' => $user['gender'],
        'height' => $user['height'],
        'weight' => $user['weight'],
        'fitness_goal' => $user['fitness_goal'],
        'activity_level' => $user['activity_level'],
        'avatar_level' => $user['avatar_level'],
        'total_workouts' => $user['total_workouts'],
        'streak_days' => $user['streak_days'],
        'total_calories_burned' => $user['total_calories_burned'],
        'achievements' => $user['achievements'],
    ];

    json_response($response);
} catch (Exception $e) {
    json_response(['error' => 'Login failed', 'details' => $e->getMessage()], 500);
}


