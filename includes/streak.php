<?php
/**
 * 连续天数（Streak）计算逻辑
 * 检查用户是否连续训练并更新streak_days
 */

function updateStreak($pdo, $userId, $workoutDate) {
    // 获取用户当前连续天数
    $stmt = $pdo->prepare('SELECT streak_days FROM users WHERE id = :id');
    $stmt->execute([':id' => $userId]);
    $user = $stmt->fetch();
    $currentStreak = (int) ($user['streak_days'] ?? 0);
    
    // 转换日期格式
    $workoutDateObj = new DateTime($workoutDate);
    $today = new DateTime('today');
    $yesterday = clone $today;
    $yesterday->modify('-1 day');
    
    $workoutDateStr = $workoutDateObj->format('Y-m-d');
    $todayStr = $today->format('Y-m-d');
    $yesterdayStr = $yesterday->format('Y-m-d');
    
    // 获取用户所有训练日期（去重，按日期降序）
    // 注意：此时已经插入了今天的记录，所以allDates包含刚插入的日期
    $stmt = $pdo->prepare('
        SELECT DISTINCT date
        FROM workouts
        WHERE user_id = :user_id
        ORDER BY date DESC
    ');
    $stmt->execute([':user_id' => $userId]);
    $allDates = $stmt->fetchAll(PDO::FETCH_COLUMN);
    
    // 移除今天刚插入的日期，因为我们要基于之前的记录计算
    $allDates = array_filter($allDates, function($date) use ($workoutDateStr) {
        return $date !== $workoutDateStr;
    });
    $allDates = array_values($allDates); // 重新索引数组
    
    // 如果这是第一次训练（移除今天记录后为空）
    if (empty($allDates)) {
        $newStreak = 1;
    } else {
        // 获取最近的训练日期
        $lastWorkoutDate = new DateTime($allDates[0]);
        $lastWorkoutDateStr = $lastWorkoutDate->format('Y-m-d');
        
        // 如果今天训练
        if ($workoutDateStr === $todayStr) {
            // 检查昨天是否训练
            if ($lastWorkoutDateStr === $yesterdayStr) {
                // 连续训练，天数+1
                $newStreak = $currentStreak + 1;
            } elseif ($lastWorkoutDateStr === $todayStr) {
                // 今天已经训练过了（不应该发生，因为已经过滤了）
                $newStreak = $currentStreak;
            } else {
                // 中断了，重新开始
                $newStreak = 1;
            }
        } elseif ($workoutDateStr === $yesterdayStr) {
            // 补录昨天的训练
            // 检查前天是否训练
            $dayBeforeYesterday = clone $yesterday;
            $dayBeforeYesterday->modify('-1 day');
            $dayBeforeYesterdayStr = $dayBeforeYesterday->format('Y-m-d');
            
            if ($lastWorkoutDateStr === $dayBeforeYesterdayStr) {
                // 连续训练
                $newStreak = $currentStreak + 1;
            } elseif ($lastWorkoutDateStr === $yesterdayStr) {
                // 昨天已经记录过了
                $newStreak = $currentStreak;
            } else {
                // 中断了，重新开始
                $newStreak = 1;
            }
        } else {
            // 补录更早的日期，不更新连续天数（因为可能已经中断，且无法准确判断）
            // 保持当前连续天数不变
            $newStreak = $currentStreak;
        }
    }
    
    // 更新数据库
    $updateStmt = $pdo->prepare('
        UPDATE users
        SET streak_days = :streak
        WHERE id = :id
    ');
    $updateStmt->execute([
        ':streak' => $newStreak,
        ':id' => $userId
    ]);
    
    return $newStreak;
}

