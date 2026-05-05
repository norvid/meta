#!/usr/bin/env python3
# OBS 工具函数模块

import yaml
import os


def load_config():
    """ 加载配置文件中的 OBS 配置 """
    config_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(config_dir, 'config.yml')
    
    if not os.path.exists(config_path):
        print(f'错误：配置文件 {config_path} 不存在')
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config.get('obs', {})
    except Exception as e:
        print(f'错误：加载配置文件失败：{str(e)}')
        return None


def get_obs_client(obs_config=None):
    """ 获取 OBS 客户端 """
    if not obs_config:
        obs_config = load_config()
    
    if not obs_config:
        return None
    
    ak = obs_config.get('ak', '')
    sk = obs_config.get('sk', '')
    server = obs_config.get('server', 'obs.cn-sound-1.myhuaweicloud.com')
    
    if not ak or not sk:
        print('错误：请在配置文件中设置 ak 和 sk')
        return None
    
    try:
        from obs import ObsClient
        return ObsClient(access_key_id=ak, secret_access_key=sk, server=server)
    except ImportError:
        print("请安装 OBS SDK: pip install esdk-obs-python")
        return None


def fix_obs_path(obs_path):
    """ 确保路径格式正确，删除首尾的 / """
    if obs_path:
        if obs_path.startswith('/'):
            obs_path = obs_path[1:]
        if obs_path.endswith('/'):
            obs_path = obs_path[:-1]
    else:
        obs_path = ''
    return obs_path


def check_bucket(client, bucket_name):
    """ 检查 bucket 是否存在 """
    try:
        resp = client.headBucket(bucket_name)
        if resp.status < 300:
            return True
        else:
            print(f'桶 {bucket_name} 不存在')
            return False
    except Exception as e:
        print(f'检测桶存在性失败：{str(e)}')
        return False


def list_files(client, bucket_name, obs_path):
    """ 列出指定 OBS 目录下的文件和子目录 """
    try:
        obs_path = fix_obs_path(obs_path)
        prefix = f"{obs_path}/" if obs_path else ''
        delimiter = "/"
        
        resp = client.listObjects(
            bucket_name, 
            prefix=prefix, 
            max_keys=500, 
            delimiter=delimiter
        )
        
        if resp.status >= 300:
            return {'success': False, 'error': resp.errorMessage}
        
        body = resp.body
        
        folders = []
        files = []
        
        for f in body.get('commonPrefixs', []):
            folder_path = f["prefix"]
            if folder_path != prefix:
                folder_name = folder_path[len(prefix):-1]
                folders.append({'name': folder_name, 'path': folder_path})
        
        for obj in body.get('contents', []):
            obj_key = obj["key"]
            if obj_key != prefix:
                file_name = obj_key[len(prefix):]
                file_size = obj.get('size', 0)
                files.append({'name': file_name, 'size': file_size, 'key': obj_key})
        
        return {
            'success': True,
            'folders': folders,
            'files': files,
            'total': len(folders) + len(files)
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def create_download_url(client, bucket_name, obs_path, expires=600):
    """ 生成带授权信息的下载对象 URL，默认 600s(10分钟)内可下载 """
    try:
        obs_path = fix_obs_path(obs_path)
        
        resp = client.createSignedUrl(
            method='GET',
            bucketName=bucket_name,
            objectKey=obs_path,
            expires=expires
        )
        
        if hasattr(resp, 'signedUrl') and resp.signedUrl:
            return {'success': True, 'url': resp.signedUrl}
        else:
            return {
                'success': False, 
                'error': getattr(resp, 'errorMessage', '生成下载 URL 失败')
            }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
