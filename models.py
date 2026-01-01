from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# 创建数据库实例
db = SQLAlchemy()

# 定义数据库模型
class Database(db.Model):
    __tablename__ = 'tb_database'
    id = db.Column(db.Integer, primary_key=True)
    db_type = db.Column(db.String(20), nullable=False)
    db_alias = db.Column(db.String(100), nullable=False)
    db_host = db.Column(db.String(100), nullable=False)
    db_port = db.Column(db.Integer, nullable=False)
    db_name = db.Column(db.String(100), nullable=False)
    db_user = db.Column(db.String(100), nullable=False)
    db_password = db.Column(db.String(100), nullable=False)
    remark = db.Column(db.String(512), nullable=True)  # 新增备注字段
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Table(db.Model):
    __tablename__ = 'tb_table'
    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer, nullable=False)
    schema_name = db.Column(db.String(64), nullable=True)
    table_name = db.Column(db.String(100), nullable=False)
    table_comment = db.Column(db.String(255))
    remark = db.Column(db.String(512))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    
    # 关系
    columns = db.relationship('Column', backref='table', lazy=True)

class Column(db.Model):
    __tablename__ = 'tb_column'
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('tb_table.id'), nullable=False)
    column_name = db.Column(db.String(100), nullable=False)
    column_type = db.Column(db.String(100), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    is_unique = db.Column(db.Boolean, default=False)
    column_comment = db.Column(db.String(255))
    ordinal_position = db.Column(db.Integer)

