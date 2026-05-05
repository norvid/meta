#!/usr/bin/env python3
# OBS 路由模块

from flask import Blueprint, render_template, jsonify, request

obs_bp = Blueprint('obs', __name__)

from .utils import load_config, get_obs_client, fix_obs_path, list_files, create_download_url


@obs_bp.app_template_filter('filesizeformat')
def filesizeformat_filter(size):
    """ 文件大小格式化 """
    if size is None or size == 0:
        return '-'
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


@obs_bp.route('/obs')
def obs_index():
    """ OBS 文件浏览首页 """
    obs_config = load_config()
    
    if not obs_config or not obs_config.get('ak') or not obs_config.get('sk'):
        return render_template('obs_config_error.html', error='OBS 配置未设置')
    
    client = get_obs_client(obs_config)
    if not client:
        return render_template('obs_config_error.html', error='无法连接 OBS 服务')
    
    bucket_name = obs_config.get('bucket', '')
    root_path = obs_config.get('root_path', 'cwdz/files/')
    current_path = request.args.get('path', '')
    
    full_path = root_path + current_path if current_path else root_path
    
    try:
        result = list_files(client, bucket_name, full_path)
        client.close()
        
        if not result['success']:
            return render_template('obs_error.html', error=result['error'])
        
        folders = []
        for folder in result['folders']:
            relative_path = current_path + '/' + folder['name'] if current_path else folder['name']
            folders.append({
                'name': folder['name'],
                'path': relative_path
            })
        
        files = result['files']
        
        parent_path = ''
        if current_path:
            parent_path = '/'.join(current_path.split('/')[:-1]) if len(current_path.split('/'))>1 else ''
        else:
            parent_path = ''
        
        return render_template('obs_browser.html',
                             folders=folders,
                             files=files,
                             current_path=current_path,
                             parent_path=parent_path,
                             root_path=root_path,
                             active_page='obs')
    
    except Exception as e:
        if client:
            client.close()
        return render_template('obs_error.html', error=str(e))


@obs_bp.route('/obs/download')
def obs_download():
    """ 生成 OBS 文件下载链接 """
    obs_config = load_config()
    
    if not obs_config or not obs_config.get('ak') or not obs_config.get('sk'):
        return jsonify({'success': False, 'message': 'OBS 配置未设置'})
    
    client = get_obs_client(obs_config)
    if not client:
        return jsonify({'success': False, 'message': '无法连接 OBS 服务'})
    
    bucket_name = obs_config.get('bucket', '')
    file_key = request.args.get('key', '')
    
    if not file_key:
        client.close()
        return jsonify({'success': False, 'message': '文件路径不能为空'})
    
    try:
        result = create_download_url(client, bucket_name, file_key, expires=600)
        client.close()
        
        if result['success']:
            return jsonify({'success': True, 'url': result['url']})
        else:
            return jsonify({'success': False, 'message': result['error']})
    
    except Exception as e:
        if client:
            client.close()
        return jsonify({'success': False, 'message': str(e)})
