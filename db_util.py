import yaml
from flask_sqlalchemy import SQLAlchemy
import pymysql

# 读取配置文件
def load_config():
    with open('config.yml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# 根据配置生成数据库连接URL
def generate_db_uri(config):
    db_config = config['database']
    db_type = db_config['type']
    
    if db_type == 'mysql':
        return f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
    elif db_type == 'postgresql':
        return f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
    elif db_type == 'sqlite':
        return f"sqlite:///{db_config['name']}"
    else:
        raise ValueError(f"不支持的数据库类型: {db_type}")

# 初始化数据库连接
def init_db(app, config, db):
    # 配置数据库连接
    app.config['SQLALCHEMY_DATABASE_URI'] = generate_db_uri(config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
