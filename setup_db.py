#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
根据配置文件config.yml连接数据库并执行create_tables.sql创建表结构和测试数据
"""

import yaml
import os
import sys
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"配置文件加载成功: {config_path}")
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        sys.exit(1)


def get_db_connection(config):
    """根据配置获取数据库连接"""
    db_config = config['database']
    db_type = db_config['type']
    
    if db_type == 'mysql':
        try:
            import pymysql
            conn = pymysql.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['name'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info(f"MySQL连接成功: {db_config['host']}:{db_config['port']}")
            return conn
        except ImportError:
            logger.error("请安装pymysql库: pip install pymysql")
            sys.exit(1)
        except Exception as e:
            logger.error(f"MySQL连接失败: {e}")
            sys.exit(1)
    
    elif db_type == 'sqlite':
        try:
            import sqlite3
            import os
            # 确保 instance 目录存在
            os.makedirs('instance', exist_ok=True)
            # 使用 instance 目录存放数据库文件，与 Flask-SQLAlchemy 保持一致
            db_path = os.path.join('instance', db_config['name'])
            conn = sqlite3.connect(db_path)
            logger.info(f"SQLite连接成功: {db_path}")
            return conn
        except Exception as e:
            logger.error(f"SQLite连接失败: {e}")
            sys.exit(1)
    
    elif db_type == 'postgresql':
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                dbname=db_config['name'],
                user=db_config['user'],
                password=db_config['password']
            )
            logger.info(f"PostgreSQL连接成功: {db_config['host']}:{db_config['port']}")
            return conn
        except ImportError:
            logger.error("请安装psycopg2库: pip install psycopg2-binary")
            sys.exit(1)
        except Exception as e:
            logger.error(f"PostgreSQL连接失败: {e}")
            sys.exit(1)
    
    else:
        logger.error(f"不支持的数据库类型: {db_type}")
        sys.exit(1)


def execute_sql_script(conn, sql_file_path):
    """执行SQL脚本文件"""
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 创建游标
        cursor = conn.cursor()
        
        # 对于SQLite，直接执行整个脚本
        if conn.__class__.__module__ == 'sqlite3':
            cursor.executescript(sql_script)
        else:
            # 处理SQL脚本，移除注释行
            lines = sql_script.split('\n')
            processed_lines = []
            for line in lines:
                # 移除行内注释
                line = line.split('--')[0].strip()
                if line:  # 只保留非空行
                    processed_lines.append(line)
            
            # 将处理后的行重新组合成脚本
            processed_script = '\n'.join(processed_lines)
            
            # 按语句执行
            sql_statements = processed_script.split(';')
            for stmt in sql_statements:
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)
        
        # 提交事务
        conn.commit()
        cursor.close()
    except Exception as e:
        logger.error(f"SQL脚本执行失败: {e}")
        conn.rollback()
        sys.exit(1)


def main():
    """主函数"""
    # 获取当前脚本所在目录
    base_dir = Path(__file__).parent
    
    # 配置文件路径
    config_path = base_dir / 'config.yml'
    
    # 检查配置文件是否存在
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        sys.exit(1)
    
    # 加载配置
    config = load_config(config_path)
    
    # 根据数据库类型选择对应的SQL脚本
    db_type = config['database']['type']
    
    # SQL脚本文件名映射
    sql_file_map = {
        'mysql': 'create_tables.mysql.sql',
        'sqlite': 'create_tables.sqlite.sql',
        'postgresql': 'create_tables.mysql.sql'  # PostgreSQL暂时使用MySQL脚本，后续可单独创建
    }
    
    # 获取SQL脚本路径
    sql_file_name = sql_file_map.get(db_type)
    sql_file_path = base_dir / 'sql' / sql_file_name
    
    # 检查SQL脚本文件是否存在
    if not sql_file_path.exists():
        logger.error(f"SQL脚本文件不存在: {sql_file_path}")
        sys.exit(1)
    
    logger.info(f"使用SQL脚本: {sql_file_name}")
    
    # 获取数据库连接
    conn = get_db_connection(config)
    
    try:
        # 执行SQL脚本
        execute_sql_script(conn, sql_file_path)
        logger.info("数据库初始化完成！")
    finally:
        # 关闭连接
        conn.close()
        logger.info("数据库连接已关闭")


if __name__ == '__main__':
    main()
