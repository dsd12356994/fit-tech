<?php
// 启用输出缓冲，防止任何输出干扰JSON响应
ob_start();

require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';
require_once __DIR__ . '/../../includes/functions.php';
require_once __DIR__ . '/../../includes/auth_check.php';
require_once __DIR__ . '/../../includes/streak.php';
require_once __DIR__ . '/../../includes/achievements.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['error' => 'Method not allowed'], 405);
}

$userId = require_login();
$data = json_input();

// 数据验证
require_fields($data, ['workout_type', 'duration_minutes', 'intensity']);

// 验证训练类型
$validTypes = ['strength', 'cardio', 'hiit', 'yoga', 'other'];
$type = $data['workout_type'];
if (!in_array($type, $validTypes)) {
    json_response(['error' => 'Invalid workout type'], 400);
}

// 验证强度
$validIntensities = ['light', 'moderate', 'hard', 'extreme'];
$intensity = $data['intensity'];
if (!in_array($intensity, $validIntensities)) {
    json_response(['error' => 'Invalid intensity level'], 400);
}

// 验证时长
$duration = (int) $data['duration_minutes'];
if ($duration < 1 || $duration > 600) {
    json_response(['error' => 'Duration must be between 1 and 600 minutes'], 400);
}

// 验证卡路里（如果提供）
$calories = null;
if (isset($data['calories_burned'])) {
    $calories = (int) $data['calories_burned'];
    if ($calories < 0 || $calories > 10000) {
        json_response(['error' => 'Calories burned must be between 0 and 10000'], 400);
    }
}

$notes = isset($data['notes']) ? trim($data['notes']) : null;
if ($notes && strlen($notes) > 1000) {
    json_response(['error' => 'Notes must be less than 1000 characters'], 400);
}

// 验证日期格式
$date = $data['date'] ?? date('Y-m-d');
if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) {
    json_response(['error' => 'Invalid date format. Use YYYY-MM-DD'], 400);
}
// 验证日期是否合理（不能是未来日期，不能太早）
$dateObj = new DateTime($date);
$today = new DateTime();
$minDate = new DateTime('2020-01-01');
if ($dateObj > $today) {
    json_response(['error' => 'Cannot log workouts for future dates'], 400);
}
if ($dateObj < $minDate) {
    json_response(['error' => 'Date is too far in the past'], 400);
}

try {
    $pdo = Database::getConnection();
    
    // 开始事务
    $pdo->beginTransaction();

    // 插入训练记录
    $stmt = $pdo->prepare('
        INSERT INTO workouts (user_id, workout_type, duration_minutes, intensity, calories_burned, notes, date, created_at)
        VALUES (:user_id, :workout_type, :duration_minutes, :intensity, :calories_burned, :notes, :date, NOW())
    ');
    $stmt->execute([
        ':user_id' => $userId,
        ':workout_type' => $type,
        ':duration_minutes' => $duration,
        ':intensity' => $intensity,
        ':calories_burned' => $calories,
        ':notes' => $notes,
        ':date' => $date,
    ]);

    // 更新用户统计字段
    $updateUser = $pdo->prepare('
        UPDATE users
        SET 
            total_workouts = total_workouts + 1,
            total_calories_burned = total_calories_burned + IFNULL(:calories_burned, 0)
        WHERE id = :id
    ');
    $updateUser->execute([
        ':calories_burned' => $calories,
        ':id' => $userId,
    ]);

    // 更新连续天数
    $newStreak = updateStreak($pdo, $userId, $date);
    
    // 检查并解锁成就
    $unlockedAchievements = checkAndUnlockAchievements($pdo, $userId);
    
    // 提交事务
    $pdo->commit();
    
    // 返回成功响应，包含解锁的成就信息
    $response = ['success' => true];
    if (!empty($unlockedAchievements)) {
        $response['achievements_unlocked'] = $unlockedAchievements;
        $response['new_streak'] = $newStreak;
    }
    
    json_response($response);
} catch (Exception $e) {
    // 回滚事务
    if (isset($pdo) && $pdo->inTransaction()) {
        $pdo->rollBack();
    }
    // 记录错误到日志（不输出到响应）
    error_log('Workout log error: ' . $e->getMessage());
    json_response(['error' => 'Failed to log workout', 'details' => $e->getMessage()], 500);
}


