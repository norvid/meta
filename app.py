from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime

# 导入数据库模型和初始化函数
from models import db, Database, Table, Column
import db_util

# 载入配置文件
config = db_util.load_config()

# 创建Flask应用, 初始化数据库连接
app = Flask(__name__)
db_util.init_db(app, config, db)

# 全局同步任务map，用于存储同步状态
import threading
sync_tasks = {}
sync_lock = threading.Lock()

# 生成6位随机token
def generate_token():
    import random, string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# 路由定义
@app.route('/')
def index():
    # 首页直接跳转到数据库列表页
    return render_template('index.html')

@app.route('/index')
def index_redirect():
    # 首页直接跳转到数据库列表页
    return render_template('index.html')

@app.route('/databases')
def databases():
    # 获取所有数据库
    databases = Database.query.all()
    # 移除密码信息
    for db in databases:
        db.db_password = ''
    return render_template('databases.html', databases=databases)

# 新增数据库路由
@app.route('/databases/add', methods=['POST'])
def add_database():
    if request.method == 'POST':
        # 获取表单数据
        db_type = request.form.get('db_type')
        db_alias = request.form.get('db_alias')
        db_host = request.form.get('db_host')
        db_port = request.form.get('db_port', type=int)
        db_name = request.form.get('db_name')
        db_user = request.form.get('db_user')
        db_password = request.form.get('db_password')
        remark = request.form.get('remark')
        
        # 验证数据
        if not all([db_type, db_alias, db_host, db_port, db_name, db_user, db_password]):
            # 如果有字段为空，重定向回数据库列表页
            return redirect(url_for('databases'))
        
        # 创建新的数据库记录
        new_database = Database(
            db_type=db_type,
            db_alias=db_alias,
            db_host=db_host,
            db_port=db_port,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
            remark=remark
        )
        
        # 保存到数据库
        db.session.add(new_database)
        db.session.commit()
        
        # 重定向回数据库列表页
        return redirect(url_for('databases'))

# 编辑数据库路由
@app.route('/databases/edit', methods=['POST'])
def edit_database():
    if request.method == 'POST':
        # 获取表单数据
        id = request.form.get('id', type=int)
        db_alias = request.form.get('db_alias')
        db_host = request.form.get('db_host')
        db_port = request.form.get('db_port', type=int)
        db_name = request.form.get('db_name')
        db_user = request.form.get('db_user')
        db_password = request.form.get('db_password')
        remark = request.form.get('remark')
        update_password = request.form.get('update_password')  # 检查是否需要更新密码
        
        # 验证基本数据（不包括密码）
        if not all([id, db_alias, db_host, db_port, db_name, db_user]):
            # 如果有字段为空，重定向回数据库列表页
            return redirect(url_for('databases'))
        
        # 根据ID查找数据库记录
        database = Database.query.get_or_404(id)
        
        # 更新基本信息
        database.db_alias = db_alias
        database.db_host = db_host
        database.db_port = db_port
        database.db_name = db_name
        database.db_user = db_user
        database.remark = remark  # 更新备注信息
        
        # 只有当需要更新密码且密码不为空时，才更新密码
        if update_password and db_password:
            database.db_password = db_password
        
        # 保存到数据库
        db.session.commit()
        
        # 重定向到本数据库的详情页
        return redirect(url_for('database_tables', db_id=id))

# 删除数据库路由
@app.route('/databases/delete', methods=['POST'])
def delete_database():
    if request.method == 'POST':
        # 获取要删除的数据库ID
        id = request.form.get('id', type=int)
        
        # 验证ID
        if not id:
            return redirect(url_for('databases'))
        
        # 根据ID查找数据库记录
        database = Database.query.get_or_404(id)
        
        # 删除记录
        db.session.delete(database)
        db.session.commit()
        
        # 重定向回数据库列表页
        return redirect(url_for('databases'))

# 测试数据库连接路由
@app.route('/databases/test-connection', methods=['POST'])
def test_database_connection():
    from meta_sync import test_database_connection as meta_test_conn
    
    try:
        # 获取表单数据
        db_type = request.form.get('db_type')
        db_host = request.form.get('db_host')
        db_port = request.form.get('db_port', type=int)
        db_name = request.form.get('db_name')
        db_user = request.form.get('db_user')
        db_password = request.form.get('db_password')
        db_id = request.form.get('id', type=int)  # 获取数据库ID
        
        # 如果密码为空且提供了数据库ID，从数据库中获取密码
        if not db_password and db_id:
            database = Database.query.get(db_id)
            if database:
                db_password = database.db_password
        
        # 调用meta_sync模块的测试连接函数
        result = meta_test_conn(db_type, db_host, db_port, db_name, db_user, db_password)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'连接失败：{str(e)}'})

@app.route('/database/<int:db_id>/tables')
def database_tables(db_id):
    # 获取数据库
    database = Database.query.get_or_404(db_id)
    # 移除密码信息
    database.db_password = ''
    
    # 获取分页参数和搜索关键字
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    per_page = 20
    
    # 构建查询
    query = Table.query.filter_by(db_id=db_id)
    
    # 如果有搜索关键字，添加搜索条件
    if keyword:
        query = query.filter(
            (Table.table_name.ilike(f'%{keyword}%')) | 
            (Table.schema_name == keyword) |  # 模式名使用完全匹配查询
            (Table.table_comment.ilike(f'%{keyword}%'))
        )
    
    # 分页获取表列表，按表名升序排序
    tables = query.order_by(Table.table_name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('tables.html', database=database, tables=tables, keyword=keyword)


@app.route('/database/<int:db_id>/table/<string:schema_name>/<string:table_name>/info')
def table_info(db_id, schema_name, table_name):
    # 获取数据库和表
    database = Database.query.get_or_404(db_id)
    # 移除密码信息
    database.db_password = ''
    table = Table.query.filter_by(db_id=db_id, schema_name=schema_name, table_name=table_name).first_or_404()
    
    # 获取表的字段
    columns = Column.query.filter_by(table_id=table.id).order_by(Column.ordinal_position).all()
    
    return render_template('table_info.html', database=database, table=table, columns=columns)

# 更新表备注路由
@app.route('/database/<int:db_id>/table/<int:table_id>/update-remark', methods=['POST'])
def update_table_remark(db_id, table_id):
    # 获取数据库和表
    database = Database.query.get_or_404(db_id)
    table = Table.query.get_or_404(table_id)
    
    # 获取新备注
    new_remark = request.form.get('remark')
    
    # 更新备注
    table.remark = new_remark
    db.session.commit()
    
    # 返回成功响应
    return jsonify({'success': True, 'message': '备注更新成功'})

# 实际执行同步的函数
def do_sync_tables(db_id, token):
    try:
        # 导入meta_sync模块的同步函数
        from meta_sync import mysql_sync_tables, postgres_sync_tables, hive_sync_tables
        
        # 创建应用上下文
        with app.app_context():
            # 获取数据库
            database = Database.query.get_or_404(db_id)
            
            # 初始化结果
            success = False
            message = ''
            
            # 根据数据库类型选择不同的同步函数
            try:
                if database.db_type == 'MySQL':
                    result = mysql_sync_tables(database, db, Table, Column)
                elif database.db_type == 'PostgreSQL':
                    result = postgres_sync_tables(database, db, Table, Column)
                elif database.db_type == 'Hive':
                    result = hive_sync_tables(database, db, Table, Column)
                else:
                    raise Exception(f'不支持的数据库类型：{database.db_type}')
                
                # 解析结果
                success = result['success']
                message = result['message']
            except Exception as e:
                # 捕获同步过程中的异常
                success = False
                message = f'同步失败：{str(e)}'
                import traceback
                traceback.print_exc()  # 输出详细堆栈信息
            
            # 输出通用日志
            print(f"[SYNC LOG] 数据库 {db_id} 同步{'成功' if success else '失败'}: {message}")
            
            # 更新同步状态，添加last_completed_at字段记录完成时间
            with sync_lock:
                sync_tasks[db_id] = {
                    'status': 'success' if success else 'error',
                    'msg': message,
                    'timestamp': datetime.now().isoformat(),
                    'last_completed_at': datetime.now().timestamp(),  # 添加完成时间戳
                    'token': token
                }
    except Exception as e:
        # 处理全局异常
        error_msg = f'同步失败：{str(e)}'
        with sync_lock:
            sync_tasks[db_id] = {
                'status': 'error',
                'msg': error_msg,
                'timestamp': datetime.now().isoformat(),
                'last_completed_at': datetime.now().timestamp(),  # 添加完成时间戳
                'token': token
            }
        # 输出日志
        print(f"[SYNC LOG] 数据库 {db_id} 同步失败 (全局异常): {error_msg}")
        import traceback
        traceback.print_exc()  # 输出详细堆栈信息

# 同步表信息路由
@app.route('/database/<int:db_id>/sync-tables', methods=['POST'])
def sync_tables(db_id):
    current_time = datetime.now().timestamp()
    cooldown_seconds = 30  # 30秒冷却期
    
    with sync_lock:
        # 检查是否已有同步任务正在执行
        if db_id in sync_tasks and sync_tasks[db_id]['status'] == 'loading':
            print(f"[SYNC LOG] 数据库 {db_id} 同步任务正在执行中，返回loading状态")
            return jsonify({
                'success': True,  # 表示请求成功，只是状态是loading
                'message': '同步任务正在执行中',
                'token': sync_tasks[db_id]['token']
            })
        
        # 检查是否已有同步任务记录
        if db_id in sync_tasks:
            task = sync_tasks[db_id]
            
            # 检查冷却期
            if 'last_completed_at' in task and task['last_completed_at'] > 0:
                last_completed = task['last_completed_at']
                time_diff = current_time - last_completed
                
                # 如果时间差小于30秒，直接返回上次结果
                if time_diff < cooldown_seconds:
                    print(f"[SYNC LOG] 数据库 {db_id} 同步冷却期内，返回上次结果")
                    return jsonify({
                        'success': task['status'] == 'success',
                        'message': task['msg'],
                        'token': task['token']
                    })
    
    # 生成token
    token = generate_token()
    
    # 初始化同步状态，添加last_completed_at字段（初始为0）
    with sync_lock:
        sync_tasks[db_id] = {
            'status': 'loading',
            'msg': '同步中...',
            'timestamp': datetime.now().isoformat(),
            'last_completed_at': 0,  # 初始化为0
            'token': token
        }
    
    # 启动异步线程执行同步
    import threading
    thread = threading.Thread(target=do_sync_tables, args=(db_id, token))
    thread.daemon = True
    thread.start()
    
    # 返回token和初始状态
    return jsonify({'success': True, 'token': token, 'message': '同步任务已启动'})

# 查询同步状态路由
@app.route('/database/<int:db_id>/sync-status', methods=['GET'])
def sync_status(db_id):
    token = request.args.get('token')
    
    with sync_lock:
        if db_id not in sync_tasks:
            return jsonify({'status': 'none'})
        
        task = sync_tasks[db_id]
        
        # 如果token一致，返回完整结果并删除记录
        if token and token == task['token']:
            result = {
                'status': task['status'],
                'msg': task['msg'],
                'timestamp': task['timestamp']
            }
            # 只有完成状态才删除记录
            if task['status'] != 'loading':
                del sync_tasks[db_id]
            return jsonify(result)
        else:
            # token不一致或没有，仅返回状态
            return jsonify({'status': task['status']})







import sys
import argparse

if __name__ == '__main__':
    try:
        # 创建数据库表（如果不存在）
        with app.app_context():
            db.create_all()
            print("数据库表创建/检查完成！")
        
        # 解析命令行参数
        parser = argparse.ArgumentParser(description='Run the Flask application')
        parser.add_argument('--port', type=int, default=config['app']['port'], help='Port to run the application on')
        parser.add_argument('--host', type=str, default=config['app']['host'], help='Host to run the application on')
        args = parser.parse_args()
        
        # 启动应用
        app.run(debug=config['app']['debug'], host=args.host, port=args.port)
    except Exception as e:
        print(f"数据库连接失败: {e}")
        sys.exit(1)