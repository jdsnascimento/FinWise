-- Criar database separada para a Evolution API
CREATE DATABASE IF NOT EXISTS evolution_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dar permissões ao root (já tem por padrão, mas para garantir)
GRANT ALL PRIVILEGES ON evolution_db.* TO 'root'@'%';
FLUSH PRIVILEGES;
