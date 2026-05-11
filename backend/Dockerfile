# 使用官方 Python 3.11 Slim 镜像（体积小）
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖（PyMuPDF 需要）
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件（利用 Docker 层缓存）
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install -r requirements.txt

# 复制源代码
COPY . .

# 创建数据库目录
RUN mkdir -p database

# 暴露端口
EXPOSE 5001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# 启动命令
CMD ["python", "run.py"]
