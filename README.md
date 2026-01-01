# 数据库元数据管理系统 - Meta

## 项目简介
Meta是一个基于Python Flask + Bootstrap 5构建的数据库元数据管理系统。它的核心功能是从MySQL、PostgreSQL、Hive、SqlServer等数据库中获取表和字段的元数据，并提供友好的界面展示和管理这些信息。

## 核心功能
- ✅ 支持多种数据库类型：MySQL、PostgreSQL、Hive、SqlServer
- ✅ 数据库列表展示与管理
- ✅ 表列表分页展示与搜索
- ✅ 表详细信息和字段列表展示
- ✅ 直观的数据库类型图标标识
- ✅ 表字段的主键和唯一索引标识
- ✅ 异步表同步功能
- ✅ 同步状态轮询显示
- ✅ 表备注编辑功能
- ✅ 字段筛选功能
- ✅ 配置文件管理数据库连接

## 技术栈
- **后端框架**：Python Flask 3.0.0
- **数据库ORM**：SQLAlchemy 3.1.1
- **数据库驱动**：PyMySQL 1.0.3（用于MySQL连接）
- **配置管理**：PyYAML 6.0.1
- **前端框架**：Bootstrap 5.3.0
- **前端图标**：Bootstrap Icons
- **数据库**：SQLite（默认，用于存储元数据）

## 项目结构
```
meta/
├── app.py                 # Flask应用主入口
├── models.py              # 数据库模型定义
├── setup_db.py            # 数据库初始化脚本
├── config.yml             # 应用配置文件
├── requirements.txt       # 项目依赖
├── .gitignore            # Git忽略文件
├── README.md             # 项目说明文档
├── templates/            # HTML模板
│   ├── index.html        # 首页
│   ├── databases.html    # 数据库列表页
│   ├── tables.html       # 表列表页
│   └── table_info.html   # 表信息页
├── sql/                  # 数据库SQL脚本
│   ├── create_tables.mysql.sql   # MySQL表结构脚本
│   └── create_tables.sqlite.sql  # SQLite表结构脚本
└── static/               # 静态资源
    ├── css/
    │   ├── bootstrap.min.css
    │   ├── bootstrap-icons.min.css
    │   └── fonts/
    │       └── bootstrap-icons.woff2
    └── js/
        └── bootstrap.bundle.min.js
```

## 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置数据库
1. 复制示例配置文件生成配置文件：
   ```bash
   cp config.yml.example config.yml
   ```

2. 编辑 `config.yml` 文件，配置应用和数据库连接：
   ```yaml
   # 应用配置
   app:
     host: '0.0.0.0'
     port: 46382
     debug: true

   # 数据库配置（以SQLite为例）
   database:
     type: 'sqlite'  # 支持 sqlite, mysql, postgresql 等
     name: 'meta.db'
   
   # MySQL配置示例
   # database:
   #   type: 'mysql'
   #   host: 'localhost'
   #   port: 3306
   #   name: 'meta'
   #   user: 'your_username'
   #   password: 'your_password'
   
   # PostgreSQL配置示例
   # database:
   #   type: 'postgresql'
   #   host: 'localhost'
   #   port: 5432
   #   name: 'meta'
   #   user: 'your_username'
   #   password: 'your_password'
   ```

### 3. 数据库初始化
执行 `setup_db.py` 脚本来初始化数据库表结构和测试数据：

```bash
python setup_db.py
```

**说明**：
- 脚本会根据 `config.yml` 中的数据库配置自动选择对应的SQL脚本
- 支持多种数据库类型：SQLite、MySQL、PostgreSQL
- 执行成功后会创建所有必要的表结构并插入测试数据

### 3. 启动应用
```bash
# 使用启动脚本启动应用（后台运行，日志自动切换）
./startup.sh

# 启动后会显示进程ID和日志文件信息
# 例如：
# 日志将增量写入：meta-app-20260101.log
# 项目已启动，进程ID：28053
# 使用以下命令查看日志：tail -f meta-app-20260101.log
# 使用以下命令停止项目：kill 28053
# 启动日志监控脚本...
# 日志监控脚本已启动
```

### 4. 停止应用
```bash
# 使用停止脚本停止应用
./shutdown.sh

# 停止后会显示停止信息
# 例如：
# 检查进程 28053 是否存在...
# 杀掉进程 28053...
# 进程 28053 已成功终止
# 删除 .app_pid 文件...
# 项目已停止
```

### 5. 查看日志
```bash
# 实时查看当前日志
# 日志文件格式：meta-app-YYYYMMDD.log
# YYYYMMDD 为当前日期，如 20260101

tail -f meta-app-$(date +%Y%m%d).log
```

应用将在配置的端口上启动，默认地址：http://127.0.0.1:46382

## 使用说明

### 首页
访问 http://127.0.0.1:46382 或 http://127.0.0.1:46382/index，将自动跳转到数据库列表页。

### 数据库列表页
- 访问 http://127.0.0.1:46382/databases
- 以卡片形式展示所有已配置的数据库
- 每个卡片显示数据库类型、别名、IP地址、端口和数据库名
- 点击数据库图标或名称跳转到该数据库的数据表页
- 点击"增加"按钮添加新数据库

### 数据表页
- 访问 http://127.0.0.1:46382/database/{db_id}/tables
- 对应的模板：`tables.html`
- 分页展示指定数据库的所有表
- 每页默认显示20个表
- 显示表的模式名、表名、表注释和创建时间
- 支持搜索表名、模式名或表注释
- 支持异步同步表信息
- 点击表名跳转到该表的详细信息页

### 表信息页
- 访问 http://127.0.0.1:46382/database/{db_id}/table/{table_id}/info
- 展示表的基本信息和备注
- 支持编辑表备注
- 展示表的所有字段信息，包括：
  - 字段名
  - 字段类型
  - KEY（主键/唯一索引）
  - 字段备注
- 支持字段搜索和筛选

## 功能使用指南

### 添加数据库
1. 在数据库列表页点击"增加"按钮
2. 填写数据库信息：
   - 数据库类型
   - 数据库别名
   - 地址和端口
   - 数据库名
   - 用户名和密码
3. 点击"测试连接"验证数据库连接
4. 点击"保存"添加数据库

### 同步表信息
1. 在数据表页点击"同步"按钮
2. 系统将异步执行表同步操作
3. 显示同步状态和进度
4. 同步完成后自动刷新页面

### 搜索表
1. 在数据表页的搜索框中输入关键字
2. 点击"查询"按钮
3. 系统将显示包含关键字的表
4. 点击"重置"按钮恢复全部表

### 编辑表备注
1. 在表信息页点击"编辑"按钮
2. 在文本框中输入备注信息
3. 点击"保存"按钮保存修改
4. 或点击"取消"按钮放弃修改

### 筛选字段
1. 在表信息页的字段筛选框中输入关键字（至少2个字符）
2. 系统将自动筛选显示包含关键字的字段
3. 清空输入框恢复所有字段

## 配置说明

### 支持的数据库类型
- **sqlite**：SQLite数据库，默认选项
- **mysql**：MySQL数据库
- **postgresql**：PostgreSQL数据库

### 配置示例

#### SQLite配置
```yaml
database:
  type: 'sqlite'
  name: 'meta.db'
```

#### MySQL配置
```yaml
database:
  type: 'mysql'
  host: 'localhost'
  port: 3306
  name: 'meta'
  user: 'root'
  password: 'password'
```

#### PostgreSQL配置
```yaml
database:
  type: 'postgresql'
  host: 'localhost'
  port: 5432
  name: 'meta'
  user: 'postgres'
  password: 'password'
```

## 开发说明

### 数据库迁移
首次启动应用时，系统将自动创建数据库表。

### 代码风格
- 使用PEP 8代码风格
- 遵循Flask最佳实践
- 代码模块化设计

## 许可证
MIT