#!/bin/bash

current_date=$(date +%Y%m%d)
log_file="meta-app-${current_date}.log"

if [ ! -f "${log_file}" ]; then
    touch "${log_file}"
fi

# 启动项目，将输出重定向到日志文件，并放到后台执行
echo "启动项目..."
echo "日志输出到：${log_file}"
python app.py >> "${log_file}" 2>&1 &

# 获取进程ID
pid=$!
echo "项目已启动，进程ID：${pid}"

# 将进程ID写入文件，方便后续管理
echo "${pid}" > .app_pid
