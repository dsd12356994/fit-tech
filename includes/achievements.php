<?php
/**
 * 成就系统辅助函数
 * 检查并解锁用户成就
 */

function checkAndUnlockAchievements($pdo, $userId) {
    // 获取用户当前统计数据
    $stmt = $pdo->prepare('
        SELECT total_workouts, total_calories_burned, streak_days
        FROM users
        WHERE id = :id
    ');
    $stmt->execute([':id' => $userId]);
    $stats = $stmt->fetch();
    
    if (!$stats) {
        return [];
    }
    
    $unlocked = [];
    $totalWorkouts = (int) $stats['total_workouts'];
    $totalCalories = (int) $stats['total_calories_burned'];
    $streakDays = (int) $stats['streak_days'];
    
    // 定义成就列表
    $achievements = [
        // 训练次数成就
        ['type' => 'first_workout', 'title' => 'First Steps', 'description' => 'Complete your first workout', 'condition' => $totalWorkouts >= 1],
        ['type' => 'workout_5', 'title' => 'Getting Started', 'description' => 'Complete 5 workouts', 'condition' => $totalWorkouts >= 5],
        ['type' => 'workout_10', 'title' => 'Dedicated', 'description' => 'Complete 10 workouts', 'condition' => $totalWorkouts >= 10],
        ['type' => 'workout_25', 'title' => 'Committed', 'description' => 'Complete 25 workouts', 'condition' => $totalWorkouts >= 25],
        ['type' => 'workout_50', 'title' => 'Elite Trainee', 'description' => 'Complete 50 workouts', 'condition' => $totalWorkouts >= 50],
        ['type' => 'workout_100', 'title' => 'Centurion', 'description' => 'Complete 100 workouts', 'condition' => $totalWorkouts >= 100],
        
        // 卡路里成就
        ['type' => 'calories_1000', 'title' => 'Calorie Burner', 'description' => 'Burn 1,000 calories', 'condition' => $totalCalories >= 1000],
        ['type' => 'calories_5000', 'title' => 'Fire Starter', 'description' => 'Burn 5,000 calories', 'condition' => $totalCalories >= 5000],
        ['type' => 'calories_10000', 'title' => 'Inferno', 'description' => 'Burn 10,000 calories', 'condition' => $totalCalories >= 10000],
        ['type' => 'calories_25000', 'title' => 'Blaze Master', 'description' => 'Burn 25,000 calories', 'condition' => $totalCalories >= 25000],
        ['type' => 'calories_50000', 'title' => 'Legendary', 'description' => 'Burn 50,000 calories', 'condition' => $totalCalories >= 50000],
        
        // 连续天数成就
        ['type' => 'streak_3', 'title' => 'Three Day Warrior', 'description' => 'Maintain a 3-day streak', 'condition' => $streakDays >= 3],
        ['type' => 'streak_7', 'title' => 'Week Warrior', 'description' => 'Maintain a 7-day streak', 'condition' => $streakDays >= 7],
        ['type' => 'streak_14', 'title' => 'Fortnight Fighter', 'description' => 'Maintain a 14-day streak', 'condition' => $streakDays >= 14],
        ['type' => 'streak_30', 'title' => 'Monthly Master', 'description' => 'Maintain a 30-day streak', 'condition' => $streakDays >= 30],
        ['type' => 'streak_100', 'title' => 'Century Streak', 'description' => 'Maintain a 100-day streak', 'condition' => $streakDays >= 100],
    ];
    
    // 检查每个成就
    foreach ($achievements as $achievement) {
        if ($achievement['condition']) {
            // 检查是否已经解锁
            $checkStmt = $pdo->prepare('
                SELECT id FROM user_achievements
                WHERE user_id = :user_id AND achievement_type = :type
            ');
            $checkStmt->execute([
                ':user_id' => $userId,
                ':type' => $achievement['type']
            ]);
            
            if (!$checkStmt->fetch()) {
                // 解锁新成就
                $insertStmt = $pdo->prepare('
                    INSERT INTO user_achievements (user_id, achievement_type, title, description, unlocked_at)
                    VALUES (:user_id, :type, :title, :description, NOW())
                ');
                $insertStmt->execute([
                    ':user_id' => $userId,
                    ':type' => $achievement['type'],
                    ':title' => $achievement['title'],
                    ':description' => $achievement['description']
                ]);
                
                // 更新用户成就计数
                $updateStmt = $pdo->prepare('
                    UPDATE users
                    SET achievements = (
                        SELECT COUNT(*) FROM user_achievements WHERE user_id = :user_id
                    )
                    WHERE id = :user_id
                ');
                $updateStmt->execute([':user_id' => $userId]);
                
                $unlocked[] = $achievement;
            }
        }
    }
    
    return $unlocked;
}

