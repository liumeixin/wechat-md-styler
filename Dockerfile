FROM python:3.11-slim

LABEL maintainer="design-shi"
LABEL description="微信公众号 Markdown 排版工具 - 交互式网页"

# 设置工作目录
WORKDIR /app

# 安装依赖
RUN pip install --no-cache-dir flask pyyaml

# 复制应用文件
COPY . .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "app.py"]