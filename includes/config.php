<?php
// ============================================
// FitTech 项目配置 - XAMPP 环境
// ============================================
// 数据库配置（XAMPP 默认设置）
define('DB_HOST', 'localhost');
define('DB_NAME', 'fittech_db');        // 确保已在 phpMyAdmin 中创建此数据库
define('DB_USER', 'root');              // XAMPP 默认用户名
define('DB_PASS', '');                  // XAMPP 默认密码为空
define('BASE_URL', 'http://localhost/fit-tech-project');

// 开启错误报告（开发环境建议打开，上线时关闭 display_errors）
error_reporting(E_ALL);
// 关闭直接显示错误，避免HTML错误信息干扰JSON响应
// 错误仍会记录到日志，但不会输出到响应中
ini_set('display_errors', 0);
ini_set('log_errors', 1);

// 会话设置
session_set_cookie_params([
    'lifetime' => 86400,
    'path' => '/',
    'domain' => '',
    'secure' => false, // 部署 HTTPS 时改为 true
    'httponly' => true,
    'samesite' => 'Lax'
]);

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// CORS 设置（允许前端跨域请求）
// 注意：只在非OPTIONS请求时设置Content-Type，避免干扰OPTIONS请求
if ($_SERVER['REQUEST_METHOD'] !== 'OPTIONS') {
    header('Content-Type: application/json; charset=utf-8');
}
header('Access-Control-Allow-Origin: http://localhost');
header('Access-Control-Allow-Credentials: true');
header('Access-Control-Allow-Headers: Content-Type');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}


