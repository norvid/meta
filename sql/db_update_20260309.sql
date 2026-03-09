-- 元数据管理系统 - 数据库增量更新脚本
-- 更新日期：2026-03-09
-- 更新内容：新增标签管理功能
-- 适用数据库：MySQL / SQLite

-- =====================================================
-- MySQL 版本
-- =====================================================

-- 创建标签表
CREATE TABLE IF NOT EXISTS `tb_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `tag_name` varchar(50) NOT NULL COMMENT '标签名称',
  `description` varchar(500) DEFAULT NULL COMMENT '标签描述',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_tag_name` (`tag_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标签表';

-- 创建表-标签关联表
CREATE TABLE IF NOT EXISTS `tb_table_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `table_id` int(11) NOT NULL COMMENT '表ID',
  `tag_id` int(11) NOT NULL COMMENT '标签ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_table_tag` (`table_id`, `tag_id`),
  KEY `idx_table_id` (`table_id`),
  KEY `idx_tag_id` (`tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表-标签关联表';

-- =====================================================
-- SQLite 版本
-- =====================================================

-- 创建标签表
-- CREATE TABLE IF NOT EXISTS `tb_tag` (
--   `id` INTEGER PRIMARY KEY AUTOINCREMENT,
--   `tag_name` TEXT NOT NULL UNIQUE,
--   `description` TEXT DEFAULT NULL,
--   `created_at` TEXT DEFAULT CURRENT_TIMESTAMP,
--   `updated_at` TEXT DEFAULT CURRENT_TIMESTAMP
-- );

-- 创建表-标签关联表
-- CREATE TABLE IF NOT EXISTS `tb_table_tag` (
--   `id` INTEGER PRIMARY KEY AUTOINCREMENT,
--   `table_id` INTEGER NOT NULL,
--   `tag_id` INTEGER NOT NULL,
--   `created_at` TEXT DEFAULT CURRENT_TIMESTAMP,
--   UNIQUE (`table_id`, `tag_id`)
-- );