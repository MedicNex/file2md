# MedicNex File2MD Docker镜像
# 基于Ubuntu 24.04，包含PaddleOCR和所有必要依赖
# 支持 ARM64 和 AMD64 架构

# Ubuntu/Debian基础镜像
FROM ubuntu:24.04
RUN apt update && apt install -y antiword

# 或者Alpine基础镜像
FROM alpine:latest
RUN apk add --no-cache antiword

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
    # 编译工具
    gcc \
    g++ \
    make \
    pkg-config \
    # 架构检测工具
    file \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 创建Python虚拟环境
RUN python3 -m venv /opt/venv

# 激活虚拟环境并升级pip
RUN /opt/venv/bin/pip install --upgrade pip setuptools wheel

# 复制requirements文件
COPY requirements.txt .

# 先安装关键依赖，避免版本冲突
RUN /opt/venv/bin/pip install "numpy>=1.26.0,<2.0" && \
    /opt/venv/bin/pip install "opencv-python-headless>=4.5,<4.9" && \
    /opt/venv/bin/pip install "opencv-python>=4.5,<4.9" && \
    /opt/venv/bin/pip install "opencv-contrib-python>=4.5,<4.9" && \
    /opt/venv/bin/pip install "protobuf>=4.0,<6.0" && \
    /opt/venv/bin/pip install "packaging<25"

# 检测架构并安装相应的PaddlePaddle版本
RUN ARCH=$(dpkg --print-architecture) && \
    echo "Detected architecture: $ARCH" && \
    if [ "$ARCH" = "arm64" ]; then \
        echo "Installing PaddlePaddle for ARM64..." && \
        /opt/venv/bin/pip install paddlepaddle -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html -i https://pypi.tuna.tsinghua.edu.cn/simple; \
    else \
        echo "Installing PaddlePaddle for AMD64..." && \
        /opt/venv/bin/pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple; \
    fi

# 安装PaddleOCR
RUN /opt/venv/bin/pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装其他项目依赖（忽略已安装的包）
RUN /opt/venv/bin/pip install --ignore-installed -r requirements.txt

# 验证依赖兼容性
RUN /opt/venv/bin/pip check || (echo "Dependency conflicts detected:" && /opt/venv/bin/pip check 2>&1 && exit 1)

# 复制应用代码
COPY app/ ./app/

# 创建必要的目录
RUN mkdir -p /app/logs /app/temp /app/.paddleocr

# 创建非root用户
RUN groupadd --system appuser && useradd --system -g appuser -d /app -s /bin/bash appuser

# 设置文件权限
RUN chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 验证安装
RUN python3 -c "import sys; print(f'Python version: {sys.version}')" && \
    python3 -c "import numpy; print(f'numpy version: {numpy.__version__}')" && \
    python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')" && \
    python3 -c "import paddle; print(f'Paddle version: {paddle.__version__}')" && \
    python3 -c "from paddleocr import PaddleOCR; print('PaddleOCR import successful')" && \
    python3 -c "import pdf2docx; print(f'pdf2docx version: {pdf2docx.__version__}')"

# 暴露端口
EXPOSE 8999

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8999/v1/health || exit 1

# 启动命令
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8999", "--workers", "1"] 