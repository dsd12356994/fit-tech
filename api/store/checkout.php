<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';
require_once __DIR__ . '/../../includes/functions.php';
require_once __DIR__ . '/../../includes/auth_check.php';

// 这里只做课程项目示例，不真正扣库存或创建订单，只是清空购物车

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['error' => 'Method not allowed'], 405);
}

$pdo = Database::getConnection();
$userId = require_login();

try {
    $stmt = $pdo->prepare('DELETE FROM cart_items WHERE user_id = :user_id');
    $stmt->execute([':user_id' => $userId]);
    json_response(['success' => true]);
} catch (Exception $e) {
    json_response(['error' => 'Failed to checkout', 'details' => $e->getMessage()], 500);
}


