-- ============================================================
-- 二手物品置换社区 - 数据库 DDL 脚本
-- 数据库: MySQL 8.0+
-- 字符集: utf8mb4
-- ============================================================

-- 如果数据库已存在则先删除，避免重复执行时出错
DROP DATABASE IF EXISTS `swap_community`;
-- 创建数据库，使用 utf8mb4 以支持完整的 Unicode（含 emoji）
CREATE DATABASE `swap_community` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `swap_community`;

-- ============================================================
-- 1. 用户表（users）
--    存储平台注册用户的基本信息以及登录所需的凭据。
-- ============================================================
CREATE TABLE `users` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户主键 ID',
    `username`      VARCHAR(50)     NOT NULL                    COMMENT '用户名，用于登录及展示，全站唯一',
    `password_hash` VARCHAR(255)    NOT NULL                    COMMENT '密码哈希值（使用 werkzeug.security 加密，不存储明文）',
    `nickname`      VARCHAR(50)     DEFAULT NULL                COMMENT '用户昵称，可与用户名不同',
    `avatar_url`    VARCHAR(500)    DEFAULT NULL                COMMENT '头像图片的 URL 或相对路径',
    `bio`           VARCHAR(500)    DEFAULT NULL                COMMENT '个人简介',
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP       COMMENT '资料更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_users_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='平台用户表';

-- ============================================================
-- 2. 物品表（items）
--    存储用户发布的二手物品信息以及期望置换的物品描述。
-- ============================================================
CREATE TABLE `items` (
    `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '物品主键 ID',
    `owner_id`        BIGINT UNSIGNED NOT NULL                COMMENT '发布者用户 ID，外键关联 users.id',
    `title`           VARCHAR(200)    NOT NULL                COMMENT '物品标题',
    `description`     TEXT            NOT NULL                COMMENT '物品详细描述（成色、使用时长、瑕疵等）',
    `images`          TEXT            DEFAULT NULL            COMMENT '物品图片列表，以 JSON 数组字符串存储多个图片路径',
    `tags`            VARCHAR(500)    DEFAULT NULL            COMMENT '物品标签，使用英文逗号分隔，例如 "数码,手机,二手"',
    `expectation`     VARCHAR(500)    DEFAULT NULL            COMMENT '期望置换的物品描述',
    `expected_tags`   VARCHAR(500)    DEFAULT NULL            COMMENT '期望置换物品的标签，英文逗号分隔，用于首页推荐匹配',
    `status`          TINYINT         NOT NULL DEFAULT 1      COMMENT '物品状态: 1=可置换, 2=置换中, 3=已完成, 4=已下架',
    `view_count`      INT UNSIGNED    NOT NULL DEFAULT 0      COMMENT '浏览次数',
    `created_at`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    `updated_at`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                      ON UPDATE CURRENT_TIMESTAMP       COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_items_owner_id`   (`owner_id`),
    KEY `idx_items_status`     (`status`),
    KEY `idx_items_created_at` (`created_at`),
    CONSTRAINT `fk_items_owner` FOREIGN KEY (`owner_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户发布的二手物品';

-- ============================================================
-- 3. 置换请求表（exchange_requests）
--    记录用户针对某物品发起的置换申请以及双方的确认进度。
-- ============================================================
CREATE TABLE `exchange_requests` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '置换请求主键 ID',
    `item_id`       BIGINT UNSIGNED NOT NULL                COMMENT '目标物品 ID，被请求置换的物品，外键关联 items.id',
    `requester_id`  BIGINT UNSIGNED NOT NULL                COMMENT '发起请求的用户 ID，外键关联 users.id',
    `message`       VARCHAR(1000)   DEFAULT NULL            COMMENT '请求附带的留言 / 自我介绍',
    `offered_item_ids` TEXT        DEFAULT NULL            COMMENT '请求方提供用于置换的物品 ID 列表，JSON 数组字符串',
    `status`        TINYINT         NOT NULL DEFAULT 0      COMMENT '请求状态: 0=待确认, 1=已接受, 2=已拒绝, 3=进行中, 4=已完成, 5=已取消',
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发起时间',
    `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP        COMMENT '状态更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_requests_item_id`      (`item_id`),
    KEY `idx_requests_requester_id` (`requester_id`),
    KEY `idx_requests_status`       (`status`),
    CONSTRAINT `fk_requests_item`      FOREIGN KEY (`item_id`)      REFERENCES `items`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_requests_requester` FOREIGN KEY (`requester_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物品置换请求与进度跟踪';

-- ============================================================
-- 4. 私信消息表（messages）
--    存储两个用户之间的一对一聊天消息，配合前端 SocketIO 实现实时聊天。
-- ============================================================
CREATE TABLE `messages` (
    `id`           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '消息主键 ID',
    `sender_id`    BIGINT UNSIGNED NOT NULL                COMMENT '发送者用户 ID',
    `receiver_id`  BIGINT UNSIGNED NOT NULL                COMMENT '接收者用户 ID',
    `content`      TEXT            NOT NULL                COMMENT '消息正文',
    `is_read`      TINYINT(1)      NOT NULL DEFAULT 0      COMMENT '是否已读: 0=未读, 1=已读',
    `created_at`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    PRIMARY KEY (`id`),
    KEY `idx_messages_sender`   (`sender_id`),
    KEY `idx_messages_receiver` (`receiver_id`),
    KEY `idx_messages_created`  (`created_at`),
    KEY `idx_messages_pair`     (`sender_id`, `receiver_id`),
    CONSTRAINT `fk_messages_sender`   FOREIGN KEY (`sender_id`)   REFERENCES `users`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_messages_receiver` FOREIGN KEY (`receiver_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户之间的私信消息';

-- ============================================================
-- 可选：初始化一个演示用户（密码为 123456，哈希由 Flask werkzeug 生成）
-- 实际项目中请在应用启动后通过注册接口创建用户。
-- ============================================================
-- INSERT INTO users (username, password_hash, nickname, bio) VALUES
-- ('demo', 'pbkdf2:sha256:260000$xxxx$yyyy', '演示用户', '这是一个演示账号');
