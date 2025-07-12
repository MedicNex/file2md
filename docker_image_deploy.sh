#!/bin/bash

# 检查镜像是否存在
if ! docker images | grep -q "medicnex-file2md:latest"; then
    echo "导入镜像..."
    docker load -i medicnex-file2md.tar
fi

# 停止并删除旧容器（如果存在）
docker stop medicnex-file2md 2>/dev/null || true
docker rm medicnex-file2md 2>/dev/null || true

# 启动新容器
docker run -d --name medicnex-file2md -p 8999:8999 \
  -v $(pwd)/.env:/app/.env \
  medicnex-file2md:latest

echo "服务已启动，访问 http://localhost:8999/docs"