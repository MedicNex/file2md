# MedicNex File2MD 独立Docker镜像
# 包含Redis和所有依赖，支持.env文件热重载
# 支持ARM64和AMD64架构

# 多阶段构建 - 构建阶段
FROM python:3.11-slim AS builder

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    pkg-config \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 升级pip并安装wheel
RUN pip install --upgrade pip setuptools wheel

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install -r requirements.txt

# 生产阶段
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PADDLEOCR_HOME=/app/.paddleocr
ENV PATH="/opt/venv/bin:$PATH"
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 设置工作目录
WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    # 系统工具
    curl \
    wget \
    ca-certificates \
    # Redis服务器
    redis-server \
    # OpenGL和图形库 (PaddleOCR需要)
    libgl1 \
    libglx0 \
    libgles2 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libx11-6 \
    libxcb1 \
    libxau6 \
    libxdmcp6 \
    # 中文字体支持
    fonts-noto-cjk \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    # 图像处理依赖
    libmagickwand-6.q16-6 \
    imagemagick \
    libcairo2 \
    libffi8 \
    # 音频处理依赖
    ffmpeg \
    libsndfile1 \
    # 清理
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 复制应用代码
COPY app/ ./app/
COPY webui/ ./webui/

# 创建必要的目录
RUN mkdir -p /app/logs /app/temp /app/.paddleocr /var/lib/redis

# 创建非root用户
RUN groupadd --system appuser && useradd --system -g appuser -d /app -s /bin/bash appuser

# 设置Redis配置
RUN echo "bind 127.0.0.1" > /etc/redis/redis.conf && \
    echo "port 6379" >> /etc/redis/redis.conf && \
    echo "dir /var/lib/redis" >> /etc/redis/redis.conf && \
    echo "appendonly yes" >> /etc/redis/redis.conf && \
    echo "appendfilename \"appendonly.aof\"" >> /etc/redis/redis.conf && \
    chown -R appuser:appuser /var/lib/redis /etc/redis

# 设置文件权限
RUN chown -R appuser:appuser /app

# 复制启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 暴露端口
EXPOSE 8999 6379

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8999/v1/health || exit 1

# 设置入口点
ENTRYPOINT ["docker-entrypoint.sh"]

# 默认命令
CMD ["start"] 