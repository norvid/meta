import traceback
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine import URL


def test_database_connection(db_type, db_host, db_port, db_name, db_user, db_password):
    """
    测试数据库连接
    """
    try:
        # 验证基本数据
        if not all([db_type, db_host, db_port, db_name, db_user, db_password]):
            return {'success': False, 'message': '连接失败：缺少必要的连接参数'}
        
        # 根据数据库类型创建连接字符串
        if db_type == 'MySQL':
            connection_string = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        elif db_type == 'PostgreSQL':
            connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        elif db_type == 'Hive':
            connection_string = f'hive://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        elif db_type == 'SqlServer':
            connection_string = f'mssql+pyodbc://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server'
        else:
            return {'success': False, 'message': f'连接失败：不支持的数据库类型 {db_type}'}
        
        # 尝试连接数据库
        engine = create_engine(connection_string, connect_args={'connect_timeout': 5})
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))  # 使用text函数转换SQL字符串
            # 如果连接成功，返回成功消息
            return {'success': True, 'message': '连接成功。'}
            
    except Exception as e:
        # 如果连接失败，返回错误消息
        error_msg = str(e)
        # 过滤掉SQLAlchemy的背景链接信息
        if 'Background on this error at:' in error_msg:
            error_msg = error_msg.split('Background on this error at:')[0].strip()
        
        # 提取更友好的错误信息
        if 'Can\'t connect to MySQL server' in error_msg or 'Connection refused' in error_msg:
            friendly_msg = '连接失败：无法连接到数据库服务器，请检查主机地址和端口是否正确'
        elif 'Access denied' in error_msg or 'Invalid password' in error_msg:
            friendly_msg = '连接失败：用户名或密码错误'
        elif 'Unknown database' in error_msg or 'database does not exist' in error_msg:
            friendly_msg = '连接失败：数据库不存在'
        elif 'timeout' in error_msg.lower():
            friendly_msg = '连接失败：连接超时，请检查网络和数据库服务'
        else:
            friendly_msg = f'连接失败：{error_msg}'
            
        return {'success': False, 'message': friendly_msg}


def mysql_sync_tables(dbCfg, db, Table, Column):
    """
    同步MySQL数据库的元数据
    """
    try:
        # 创建连接字符串
        connection_url = URL.create(
            drivername= "mysql+pymysql",
            username=dbCfg.db_user, password=dbCfg.db_password,
            host=dbCfg.db_host, port=dbCfg.db_port,
            database=dbCfg.db_name
        )
        
        # 连接到information_schema
        engine = create_engine(connection_url, connect_args={'connect_timeout': 10})
        
        # 查询该数据库的所有表信息
        with engine.connect() as conn:
            # 获取表信息
            tables_query = text("SELECT TABLE_NAME, TABLE_COMMENT, CREATE_TIME, UPDATE_TIME FROM information_schema.TABLES WHERE TABLE_SCHEMA = :db_name ORDER BY TABLE_NAME")
            tables_result = conn.execute(tables_query, {'db_name': dbCfg.db_name})
            tables_data = tables_result.fetchall()
            
            # 统计同步结果
            new_tables = 0
            updated_tables = 0
            total_columns = 0
            
            # 处理每张表
            for table_row in tables_data:
                table_name, table_comment, create_time, update_time = table_row # 提取表信息
                
                # 查找或创建表记录
                existing_table = Table.query.filter_by(db_id=dbCfg.id, table_name=table_name).first()
                
                if existing_table:
                    # 更新现有表
                    existing_table.schema_name = dbCfg.db_name
                    existing_table.table_comment = table_comment
                    existing_table.create_time = create_time
                    existing_table.update_time = update_time
                    updated_tables += 1
                    current_table = existing_table
                else:
                    # 创建新表
                    new_table = Table(
                        db_id=dbCfg.id,
                        schema_name = dbCfg.db_name, # MySQL不细分schema
                        table_name=table_name,
                        table_comment=table_comment,
                        create_time=create_time,
                        update_time=update_time
                    )
                    db.session.add(new_table)
                    db.session.flush()  # 获取新表的ID
                    new_tables += 1
                    current_table = new_table
                
                # 查询表的字段信息
                columns_query = text("SELECT COLUMN_NAME, COLUMN_TYPE, CASE WHEN COLUMN_KEY = 'PRI' THEN 1 ELSE 0 END AS IS_PRIMARY, CASE WHEN COLUMN_KEY = 'UNI' THEN 1 ELSE 0 END AS IS_UNIQUE, COLUMN_COMMENT, ORDINAL_POSITION FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = :db_name AND TABLE_NAME = :table_name ORDER BY ORDINAL_POSITION")
                columns_result = conn.execute(columns_query, {'db_name': dbCfg.db_name, 'table_name': table_name})
                columns_data = columns_result.fetchall()
                
                # 获取现有字段列表
                existing_columns = Column.query.filter_by(table_id=current_table.id).all()
                existing_column_names = {col.column_name for col in existing_columns}
                
                # 处理每个字段
                for col_row in columns_data:
                    column_name, column_type, is_primary, is_unique, column_comment, ordinal_position = col_row # 提取列信息
                    
                    # 查找或创建字段记录
                    existing_column = Column.query.filter_by(table_id=current_table.id, column_name=column_name).first()
                    
                    if existing_column:
                        # 更新现有字段
                        existing_column.column_type = column_type
                        existing_column.is_primary = bool(is_primary)
                        existing_column.is_unique = bool(is_unique)
                        existing_column.column_comment = column_comment
                        existing_column.ordinal_position = ordinal_position
                    else:
                        # 创建新字段
                        new_column = Column(
                            table_id=current_table.id,
                            column_name=column_name,
                            column_type=column_type,
                            is_primary=bool(is_primary),
                            is_unique=bool(is_unique),
                            column_comment=column_comment,
                            ordinal_position=ordinal_position
                        )
                        db.session.add(new_column)
                    
                    # 从现有字段集合中移除已处理的字段
                    if column_name in existing_column_names:
                        existing_column_names.remove(column_name)
                    
                    total_columns += 1
                
                # 删除不再存在的字段
                for col_name in existing_column_names:
                    column_to_delete = Column.query.filter_by(table_id=current_table.id, column_name=col_name).first()
                    if column_to_delete:
                        db.session.delete(column_to_delete)
            
            # 提交所有更改
            db.session.commit()
            
            # 返回成功消息
            return {'success': True, 'message': f'同步完成！新增表{new_tables}张，更新表{updated_tables}张，处理字段{total_columns}个'}
            
    except Exception as e:
        # 回滚事务
        db.session.rollback()
        
        # 记录错误信息
        error_msg = str(e)
        print(f"同步表信息错误: {error_msg}")
        print(traceback.format_exc())
        
        # 返回错误消息
        return {'success': False, 'message': f'同步失败：{error_msg}'}


def postgres_sync_tables(dbCfg, db, Table, Column):
    """
    同步 PostgreSQL 数据库的元数据
    """
    try:
        # 创建连接字符串
        connection_url = URL.create(
            drivername= "postgresql",
            username=dbCfg.db_user, password=dbCfg.db_password,
            host=dbCfg.db_host, port=dbCfg.db_port,
            database=dbCfg.db_name
        )
        
        # 连接到information_schema
        engine = create_engine(connection_url, connect_args={'connect_timeout': 10})
        
        # 查询该数据库的所有表信息.PG不记录表创建时间
        with engine.connect() as conn:
            # 获取表信息
            tables_query = text("""
            SELECT t.table_schema as schema_name, t.table_name, obj_description(c.oid, 'pg_class') AS table_comment, null as create_time, null as update_time
            FROM information_schema.tables t
            JOIN pg_class c ON c.relname = t.table_name
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE t.table_schema = :db_name
                AND t.table_type = 'BASE TABLE'
                AND n.nspname = t.table_schema
            ORDER BY t.table_name
            """)
            tables_result = conn.execute(tables_query, {'db_name': 'public'}) # pg 的schema都设置成 public
            tables_data = tables_result.fetchall()
            
            # 统计同步结果
            new_tables = 0
            updated_tables = 0
            total_columns = 0
            
            # 处理每张表
            for table_row in tables_data:
                schema_name, table_name, table_comment, create_time, update_time = table_row # 提取表信息
                
                # 查找或创建表记录
                existing_table = Table.query.filter_by(db_id=dbCfg.id, table_name=table_name).first()
                
                if existing_table:
                    # 更新现有表
                    existing_table.schema_name = schema_name
                    existing_table.table_comment = table_comment
                    existing_table.update_time = update_time
                    updated_tables += 1
                    current_table = existing_table
                else:
                    # 创建新表
                    new_table = Table(
                        db_id=dbCfg.id,
                        schema_name=schema_name,
                        table_name=table_name,
                        table_comment=table_comment,
                        create_time=create_time,
                        update_time=update_time
                    )
                    db.session.add(new_table)
                    db.session.flush()  # 获取新表的ID
                    new_tables += 1
                    current_table = new_table
                
                # 查询表的字段信息
                columns_query = text("""
                SELECT c.column_name,
                    c.udt_name ||
                        CASE
                            WHEN c.character_maximum_length IS NOT NULL THEN '(' || c.character_maximum_length || ')'
                            WHEN c.numeric_precision IS NOT NULL AND c.numeric_scale IS NOT NULL THEN '(' || c.numeric_precision || ',' || c.numeric_scale || ')'
                            WHEN c.datetime_precision IS NOT NULL THEN '(' || c.datetime_precision || ')'
                            ELSE ''
                        END AS column_type,
                    CASE WHEN pk_columns.column_name IS NOT NULL THEN 1 ELSE 0 END AS is_primary,
                    CASE WHEN uq_columns.column_name IS NOT NULL THEN 1 ELSE 0 END AS is_unique,
                    col_description(cls.oid, c.ordinal_position::int) AS column_comment,
                    c.ordinal_position
                FROM information_schema.columns c
                JOIN pg_class cls ON cls.relname = c.table_name
                JOIN pg_namespace ns ON ns.oid = cls.relnamespace AND ns.nspname = c.table_schema
                LEFT JOIN (
                    SELECT a.attname AS column_name
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    JOIN pg_class tbl ON tbl.oid = i.indrelid
                    JOIN pg_namespace nsp ON nsp.oid = tbl.relnamespace
                    WHERE i.indisprimary AND nsp.nspname = :schema_name AND tbl.relname = :table_name
                ) pk_columns ON pk_columns.column_name = c.column_name
                LEFT JOIN (
                    SELECT a.attname AS column_name
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    JOIN pg_class tbl ON tbl.oid = i.indrelid
                    JOIN pg_namespace nsp ON nsp.oid = tbl.relnamespace
                    WHERE i.indisunique AND NOT i.indisprimary AND array_length(i.indkey, 1) = 1 AND nsp.nspname = :schema_name AND tbl.relname = :table_name
                ) uq_columns ON uq_columns.column_name = c.column_name
                WHERE c.table_schema = :schema_name AND c.table_name = :table_name
                ORDER BY c.ordinal_position
                """)
                columns_result = conn.execute(columns_query, {'schema_name': schema_name, 'table_name': table_name})
                columns_data = columns_result.fetchall()
                
                # 获取现有字段列表
                existing_columns = Column.query.filter_by(table_id=current_table.id).all()
                existing_column_names = {col.column_name for col in existing_columns}
                
                # 处理每个字段
                for col_row in columns_data:
                    column_name, column_type, is_primary, is_unique, column_comment, ordinal_position = col_row # 提取列信息
                    
                    # 查找或创建字段记录
                    existing_column = Column.query.filter_by(table_id=current_table.id, column_name=column_name).first()
                    
                    if existing_column:
                        # 更新现有字段
                        existing_column.column_type = column_type
                        existing_column.is_primary = bool(is_primary)
                        existing_column.is_unique = bool(is_unique)
                        existing_column.column_comment = column_comment
                        existing_column.ordinal_position = ordinal_position
                    else:
                        # 创建新字段
                        new_column = Column(
                            table_id=current_table.id,
                            column_name=column_name,
                            column_type=column_type,
                            is_primary=bool(is_primary),
                            is_unique=bool(is_unique),
                            column_comment=column_comment,
                            ordinal_position=ordinal_position
                        )
                        db.session.add(new_column)
                    
                    # 从现有字段集合中移除已处理的字段
                    if column_name in existing_column_names:
                        existing_column_names.remove(column_name)
                    
                    total_columns += 1
                
                # 删除不再存在的字段
                for col_name in existing_column_names:
                    column_to_delete = Column.query.filter_by(table_id=current_table.id, column_name=col_name).first()
                    if column_to_delete:
                        db.session.delete(column_to_delete)
            
            # 提交所有更改
            db.session.commit()
            
            # 返回成功消息
            return {'success': True, 'message': f'同步完成！新增表{new_tables}张，更新表{updated_tables}张，处理字段{total_columns}个'}
            
    except Exception as e:
        # 回滚事务
        db.session.rollback()
        
        # 记录错误信息
        error_msg = str(e)
        print(f"同步表信息错误: {error_msg}")
        print(traceback.format_exc())
        
        # 返回错误消息
        return {'success': False, 'message': f'同步失败：{error_msg}'}


def hive_sync_tables(dbCfg, db, Table, Column):
    """
    同步 数仓hivemetastore 的元数据
    """
    try:
        # 创建连接字符串
        connection_url = URL.create(
            drivername= "mysql+pymysql",
            username=dbCfg.db_user, password=dbCfg.db_password,
            host=dbCfg.db_host, port=dbCfg.db_port,
            database=dbCfg.db_name
        )
        
        # 连接到information_schema
        engine = create_engine(connection_url, connect_args={'connect_timeout': 10})
        
        # 查询该数据库的所有表信息
        with engine.connect() as conn:
            # 获取表信息
            tables_query = text("""
            SELECT t.tbl_id table_id
                , d.NAME AS schema_name
                , t.TBL_NAME AS table_name
                , c.param_value as table_comment
                , from_unixtime(t.create_time) as create_time
                , null as update_time
            FROM TBLS t
            JOIN  DBS d ON t.DB_ID = d.DB_ID
            left join table_params c on t.tbl_id=c.tbl_id and c.param_key='comment'
            ORDER BY d.NAME, t.TBL_NAME
            """)
            tables_result = conn.execute(tables_query)
            tables_data = tables_result.fetchall()
            
            # 统计同步结果
            new_tables = 0
            updated_tables = 0
            total_columns = 0
            
            # 处理每张表
            for table_row in tables_data:
                table_id, schema_name, table_name, table_comment, create_time, update_time = table_row # 提取表信息
                
                # 查找或创建表记录
                existing_table = Table.query.filter_by(db_id=dbCfg.id, table_name=table_name).first()
                
                if existing_table:
                    # 更新现有表
                    existing_table.table_comment = table_comment
                    updated_tables += 1
                    current_table = existing_table
                else:
                    # 创建新表
                    new_table = Table(
                        db_id=dbCfg.id,
                        schema_name=schema_name,
                        table_name=table_name,
                        table_comment=table_comment,
                        create_time=create_time,
                        update_time=update_time
                    )
                    db.session.add(new_table)
                    db.session.flush()  # 获取新表的ID
                    new_tables += 1
                    current_table = new_table
                
                # 查询表的字段信息
                columns_query = text("""
                SELECT
                    c.COLUMN_NAME,
                    c.TYPE_NAME AS column_type,
                    0 AS is_partition,
                    c.COMMENT AS column_comment,
                    c.INTEGER_IDX AS ordinal_position
                FROM TBLS t
                JOIN DBS d ON t.DB_ID = d.DB_ID
                JOIN SDS s ON t.SD_ID = s.SD_ID
                JOIN COLUMNS_V2 c ON s.CD_ID = c.CD_ID
                WHERE t.TBL_ID = :tbl_id
                UNION ALL
                SELECT
                    pk.PKEY_NAME AS COLUMN_NAME,
                    pk.PKEY_TYPE AS column_type,
                    1 AS is_partition,
                    NULL AS column_comment,  -- 分区列注释通常不存（或需另查）
                    990 + pk.INTEGER_IDX AS ordinal_position  -- 放在普通列之后
                FROM TBLS t
                JOIN PARTITION_KEYS pk ON pk.TBL_ID = t.TBL_ID
                WHERE t.TBL_ID = :tbl_id
                ORDER BY ordinal_position
                """)
                columns_result = conn.execute(columns_query, {'tbl_id': table_id})
                columns_data = columns_result.fetchall()
                
                # 获取现有字段列表
                existing_columns = Column.query.filter_by(table_id=current_table.id).all()
                existing_column_names = {col.column_name for col in existing_columns}
                
                # 处理每个字段
                for col_row in columns_data:
                    column_name, column_type, is_partition, column_comment, ordinal_position = col_row # 提取列信息
                    
                    # 查找或创建字段记录
                    existing_column = Column.query.filter_by(table_id=current_table.id, column_name=column_name).first()
                    
                    if existing_column:
                        # 更新现有字段
                        existing_column.column_type = column_type
                        existing_column.is_partition = bool(is_partition)
                        existing_column.column_comment = column_comment
                        existing_column.ordinal_position = ordinal_position
                    else:
                        # 创建新字段
                        new_column = Column(
                            table_id=current_table.id,
                            column_name=column_name,
                            column_type=column_type,
                            is_partition=bool(is_partition),
                            column_comment=column_comment,
                            ordinal_position=ordinal_position
                        )
                        db.session.add(new_column)
                    
                    # 从现有字段集合中移除已处理的字段
                    if column_name in existing_column_names:
                        existing_column_names.remove(column_name)
                    
                    total_columns += 1
                
                # 删除不再存在的字段
                for col_name in existing_column_names:
                    column_to_delete = Column.query.filter_by(table_id=current_table.id, column_name=col_name).first()
                    if column_to_delete:
                        db.session.delete(column_to_delete)
            
            # 提交所有更改
            db.session.commit()
            
            # 返回成功消息
            return {'success': True, 'message': f'同步完成！新增表{new_tables}张，更新表{updated_tables}张，处理字段{total_columns}个'}
            
    except Exception as e:
        # 回滚事务
        db.session.rollback()
        
        # 记录错误信息
        error_msg = str(e)
        print(f"同步表信息错误: {error_msg}")
        print(traceback.format_exc())
        
        # 返回错误消息
        return {'success': False, 'message': f'同步失败：{error_msg}'}
