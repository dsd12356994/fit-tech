<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';
require_once __DIR__ . '/../../includes/functions.php';
require_once __DIR__ . '/../../includes/auth_check.php';

$pdo = Database::getConnection();
$userId = require_login();

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    header('Content-Type: application/json');
    try {
        $stmt = $pdo->prepare('
            SELECT ci.id, ci.product_id, ci.quantity, p.name, p.price
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = :user_id
        ');
        $stmt->execute([':user_id' => $userId]);
        $items = $stmt->fetchAll() ?: [];
        echo json_encode($items);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['error' => 'Failed to load cart', 'details' => $e->getMessage()]);
    }
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_input();
    require_fields($data, ['action', 'product_id']);

    $action = $data['action'];
    $productId = (int) $data['product_id'];
    $quantity = isset($data['quantity']) ? (int) $data['quantity'] : 1;

    try {
        if ($action === 'add') {
            $stmt = $pdo->prepare('
                INSERT INTO cart_items (user_id, product_id, quantity, added_at)
                VALUES (:user_id, :product_id, :quantity, NOW())
                ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
            ');
            $stmt->execute([
                ':user_id' => $userId,
                ':product_id' => $productId,
                ':quantity' => $quantity,
            ]);
        } elseif ($action === 'update') {
            $stmt = $pdo->prepare('
                UPDATE cart_items SET quantity = :quantity
                WHERE user_id = :user_id AND product_id = :product_id
            ');
            $stmt->execute([
                ':quantity' => max(1, $quantity),
                ':user_id' => $userId,
                ':product_id' => $productId,
            ]);
        } elseif ($action === 'remove') {
            $stmt = $pdo->prepare('
                DELETE FROM cart_items
                WHERE user_id = :user_id AND product_id = :product_id
            ');
            $stmt->execute([
                ':user_id' => $userId,
                ':product_id' => $productId,
            ]);
        } else {
            json_response(['error' => 'Invalid action'], 400);
        }

        json_response(['success' => true]);
    } catch (Exception $e) {
        json_response(['error' => 'Failed to modify cart', 'details' => $e->getMessage()], 500);
    }
}

json_response(['error' => 'Method not allowed'], 405);


