#!/bin/bash
pid_file=".app_pid"

# 检查PID文件是否存在
if [ ! -f "${pid_file}" ]; then
    echo "错误：${pid_file} 文件不存在，项目可能未启动或已停止"
    exit 1
fi

# 读取进程ID
pid=$(cat "${pid_file}")

# 检查进程ID是否有效
if [ -z "${pid}" ]; then
    echo "错误：${pid_file} 文件内容为空"
    rm -f "${pid_file}"
    exit 1
fi

# 检查进程是否存在
if ps -p "${pid}" > /dev/null 2>&1; then
    # 杀掉进程
    echo "杀掉进程 ${pid}..."
    kill "${pid}"
    
    # 等待进程终止
    sleep 1
    
    # 再次检查进程是否还存在
    if ps -p "${pid}" > /dev/null 2>&1; then
        echo "警告：进程 ${pid} 无法正常终止，尝试强制杀死..."
        kill -9 "${pid}"
        sleep 1
    fi
    
    # 检查最终状态
    if ps -p "${pid}" > /dev/null 2>&1; then
        echo "错误：无法杀死进程 ${pid}"
        exit 1
    else
        echo "进程 ${pid} 已成功终止"
    fi
else
    echo "警告：进程 ${pid} 不存在，可能已终止"
fi

# 删除PID文件
rm -f "${pid_file}"
echo "项目已停止"
