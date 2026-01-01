-- 创建tb_database表
CREATE TABLE if not exists `tb_database` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `db_type` varchar(20) NOT NULL COMMENT '数据库类型(MySQL、PostgreSQL、Hive、SqlServer)',
  `db_alias` varchar(100) NOT NULL COMMENT '数据库别名(中文)',
  `db_host` varchar(100) NOT NULL COMMENT '数据库IP地址',
  `db_port` int(11) NOT NULL COMMENT '数据库端口',
  `db_name` varchar(100) NOT NULL COMMENT '数据库名',
  `db_user` varchar(100) NOT NULL COMMENT '数据库用户名',
  `db_password` varchar(100) NOT NULL COMMENT '数据库密码',
  `remark` varchar(512) DEFAULT NULL COMMENT '数据库备注信息',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据库连接信息表';

-- 创建tb_table表
CREATE TABLE if not exists `tb_table` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `db_id` int(11) NOT NULL COMMENT '数据库ID',
  `schema_name` varchar(64) DEFAULT NULL COMMENT '模式名',
  `table_name` varchar(100) NOT NULL COMMENT '表名',
  `table_comment` varchar(255) DEFAULT NULL COMMENT '表注释',
  `remark` varchar(512) DEFAULT NULL COMMENT '表备注',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_db_id` (`db_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表信息表';

-- 创建tb_column表
CREATE TABLE if not exists`tb_column` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `table_id` int(11) NOT NULL COMMENT '表ID',
  `column_name` varchar(100) NOT NULL COMMENT '字段名',
  `column_type` varchar(100) NOT NULL COMMENT '字段类型',
  `is_primary` tinyint(1) DEFAULT '0' COMMENT '是否主键(0:否,1:是)',
  `is_unique` tinyint(1) DEFAULT '0' COMMENT '是否唯一索引(0:否,1:是)',
  `column_comment` varchar(255) DEFAULT NULL COMMENT '字段备注',
  `ordinal_position` int(11) DEFAULT NULL COMMENT '字段顺序',
  PRIMARY KEY (`id`),
  KEY `idx_table_id` (`table_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='字段信息表';

-- 插入测试数据
INSERT INTO `tb_database` (`db_type`, `db_alias`, `db_host`, `db_port`, `db_name`, `db_user`, `db_password`) VALUES
('MySQL', '测试MySQL数据库', '127.0.0.1', 3306, 'testdb', 'root', 'password'),
('PostgreSQL', '测试PostgreSQL数据库', '127.0.0.1', 5432, 'testdb', 'postgres', 'password'),
('Hive', '测试Hive数据库', '127.0.0.1', 10000, 'default', 'hive', 'password'),
('SqlServer', '测试SqlServer数据库', '127.0.0.1', 1433, 'testdb', 'sa', 'Password123!');

-- 插入测试表数据
INSERT INTO `tb_table` (`db_id`, `schema_name`, `table_name`, `table_comment`, `remark`, `create_time`, `update_time`) VALUES
(1, 'public', 'users', '用户表', '用户信息管理表', '2023-01-01 10:00:00', '2023-01-02 15:30:00'),
(1, 'public', 'orders', '订单表', '订单信息管理表', '2023-01-03 09:00:00', '2023-01-04 14:20:00'),
(2, 'public', 'products', '产品表', '产品信息管理表', '2023-01-05 11:00:00', '2023-01-06 16:10:00');

-- 插入测试字段数据
INSERT INTO `tb_column` (`table_id`, `column_name`, `column_type`, `is_primary`, `is_unique`, `column_comment`, `ordinal_position`) VALUES
(1, 'id', 'int(11)', 1, 1, '用户ID', 1),
(1, 'username', 'varchar(50)', 0, 1, '用户名', 2),
(1, 'email', 'varchar(100)', 0, 1, '邮箱', 3),
(1, 'password', 'varchar(255)', 0, 0, '密码', 4),
(1, 'created_at', 'datetime', 0, 0, '创建时间', 5),
(2, 'id', 'int(11)', 1, 1, '订单ID', 1),
(2, 'user_id', 'int(11)', 0, 0, '用户ID', 2),
(2, 'product_id', 'int(11)', 0, 0, '产品ID', 3),
(2, 'quantity', 'int(11)', 0, 0, '数量', 4),
(2, 'total_price', 'decimal(10,2)', 0, 0, '总价格', 5),
(3, 'id', 'serial', 1, 1, '产品ID', 1),
(3, 'product_name', 'varchar(100)', 0, 0, '产品名称', 2),
(3, 'price', 'numeric(10,2)', 0, 0, '价格', 3),
(3, 'stock', 'integer', 0, 0, '库存', 4);