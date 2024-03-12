# 第一阶段：构建环境
FROM python:3.12 AS build

# 添加项目源代码
ADD ./ /data/app/

# 设置工作目录
WORKDIR /data/app/

# 安装Python依赖（不保存缓存）
RUN pip install --no-cache-dir -r requirements.txt

# 第二阶段：运行环境
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 将第一阶段构建的依赖复制到运行环境
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /data/app .

# CMD 命令保持不变
CMD [ "python3", "./app.py" ]