<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/database.php';

header('Content-Type: application/json');

$category = $_GET['category'] ?? null;

try {
    $pdo = Database::getConnection();
    if ($category) {
        $stmt = $pdo->prepare('SELECT * FROM products WHERE category = :category ORDER BY created_at DESC');
        $stmt->execute([':category' => $category]);
    } else {
        $stmt = $pdo->query('SELECT * FROM products ORDER BY created_at DESC');
    }

    $products = $stmt->fetchAll() ?: [];
    echo json_encode($products);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to load products', 'details' => $e->getMessage()]);
}


