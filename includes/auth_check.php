<?php
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/functions.php';

function require_login(): int
{
    if (!isset($_SESSION['user_id'])) {
        json_response(['error' => 'Authentication required'], 401);
    }
    return (int) $_SESSION['user_id'];
}


