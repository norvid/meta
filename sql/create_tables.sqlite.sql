-- SQLite数据库初始化脚本
-- 创建tb_database表
CREATE TABLE if not exists `tb_database` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `db_type` TEXT NOT NULL,
  `db_alias` TEXT NOT NULL,
  `db_host` TEXT NOT NULL,
  `db_port` INTEGER NOT NULL,
  `db_name` TEXT NOT NULL,
  `db_user` TEXT NOT NULL,
  `db_password` TEXT NOT NULL,
  `remark` TEXT DEFAULT NULL,
  `created_at` TEXT DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 创建tb_table表
CREATE TABLE if not exists `tb_table` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `db_id` INTEGER NOT NULL,
  `schema_name` TEXT DEFAULT NULL,
  `table_name` TEXT NOT NULL,
  `table_comment` TEXT DEFAULT NULL,
  `remark` TEXT DEFAULT NULL,
  `create_time` TEXT DEFAULT NULL,
  `update_time` TEXT DEFAULT NULL
);

-- 创建tb_column表
CREATE TABLE if not exists `tb_column` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `table_id` INTEGER NOT NULL,
  `column_name` TEXT NOT NULL,
  `column_type` TEXT NOT NULL,
  `is_primary` INTEGER DEFAULT 0,
  `is_unique` INTEGER DEFAULT 0,
  `column_comment` TEXT DEFAULT NULL,
  `ordinal_position` INTEGER DEFAULT NULL
);


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
