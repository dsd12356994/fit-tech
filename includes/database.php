<?php
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/functions.php';

class Database
{
    private static ?PDO $instance = null;

    public static function getConnection(): PDO
    {
        if (self::$instance === null) {
            $dsn = 'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4';
            $options = [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            ];

            try {
                self::$instance = new PDO($dsn, DB_USER, DB_PASS, $options);
            } catch (PDOException $e) {
                // 记录错误到日志
                error_log('Database connection failed: ' . $e->getMessage());
                json_response(['error' => 'Database connection failed', 'details' => $e->getMessage()], 500);
            }
        }

        return self::$instance;
    }
}


