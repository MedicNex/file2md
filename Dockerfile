# MedicNex File2MD Docker镜像
# 基于Ubuntu 24.04，包含PaddleOCR和所有必要依赖

FROM ubuntu:24.04

LABEL maintainer="MedicNex"
LABEL description="File2MD API Service"
LABEL version="1.0.0"

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PADDLEOCR_HOME=/app/.paddleocr
ENV PATH=/opt/venv/bin:$PATH
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 设置工作目录
WORKDIR /app

# 更新系统包列表并安装基础依赖
RUN apt-get update && apt-get install -y \
    # Python基础依赖
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    # 系统工具
    curl \
    wget \
    jq \
    ca-certificates \
    # OpenGL和图形库 (PaddleOCR需要)
    libgl1 \
    libglx0 \
    libgles2 \
    mesa-utils \
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
    libmagickwand-dev \
    imagemagick \
    libcairo2-dev \
    libffi-dev \
    # 音频处理依赖
    ffmpeg \
    libsndfile1 \
    # 其他依赖
    gcc \
    g++ \
    make \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 创建Python虚拟环境
RUN python3 -m venv /opt/venv

# 激活虚拟环境并升级pip
RUN /opt/venv/bin/pip install --upgrade pip setuptools wheel

# 复制requirements文件并安装Python依赖
COPY requirements.txt .

# 分阶段安装Python依赖，先安装PaddlePaddle
RUN /opt/venv/bin/pip install paddlepaddle==2.6.1 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装OpenCV (无头版本，适合服务器环境)
RUN /opt/venv/bin/pip install opencv-python-headless==4.8.1.78

# 安装PaddleOCR
RUN /opt/venv/bin/pip install paddleocr==2.7.3 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装其他项目依赖
RUN /opt/venv/bin/pip install -r requirements.txt

# 复制应用代码
COPY app/ ./app/

# 创建必要的目录
RUN mkdir -p /app/logs /app/temp /app/.paddleocr

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /bin/bash appuser

# 设置文件权限
RUN chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 验证PaddleOCR安装
RUN python -c "import paddle; print(f'Paddle version: {paddle.__version__}')" && \
    python -c "from paddleocr import PaddleOCR; print('PaddleOCR import successful')"

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/v1/health || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"] 