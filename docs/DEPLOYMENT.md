# vLLM Manager 部署文档

## 1. 部署方式概览

支持三种部署方式：
1. **Docker Compose 部署**（推荐）- 一键启动，环境隔离
2. **手动部署** - 适合开发和自定义环境
3. **生产环境部署** - 高可用配置

## 2. 系统要求

### 硬件要求
- **CPU**: 4核+
- **内存**: 16GB+（运行大模型需要更多）
- **磁盘**: 100GB+ SSD（模型文件占用空间大）
- **GPU**: NVIDIA GPU（可选，用于模型推理）

### 软件要求
- **OS**: Linux (Ubuntu 20.04+ / CentOS 8+) / macOS / Windows WSL2
- **Docker**: 20.10+ (Docker Compose 部署)
- **Python**: 3.10+ (手动部署)
- **Node.js**: 18+ (手动部署)
- **NVIDIA Driver**: 525+ (GPU 支持)

## 3. Docker Compose 部署（推荐）

### 3.1 快速开始

```bash
# 1. 克隆项目
git clone <repository-url>
cd vllm_manager

# 2. 启动服务
docker-compose up -d

# 3. 访问服务
# 前端: http://localhost:3000
# 后端 API: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 3.2 Docker Compose 配置

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: vllm-manager-backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - model-cache:/app/model_cache
    environment:
      - MODEL_CACHE_DIR=/app/model_cache
      - DATABASE_URL=sqlite:///app/data/vllm_manager.db
      - VLLM_PORT_RANGE_START=8001
      - VLLM_PORT_RANGE_END=8100
    networks:
      - vllm-network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: vllm-manager-frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    depends_on:
      - backend
    networks:
      - vllm-network
    restart: unless-stopped

volumes:
  model-cache:
    driver: local

networks:
  vllm-network:
    driver: bridge
```

### 3.3 Dockerfile

#### 后端 Dockerfile (`backend/Dockerfile`)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/model_cache

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main.py"]
```

#### 前端 Dockerfile (`frontend/Dockerfile`)

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package.json
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建
RUN npm run build

# 运行阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Nginx 配置 (`frontend/nginx.conf`)

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # 前端路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3.4 GPU 支持

如需 GPU 支持，修改 `docker-compose.yml`:

```yaml
services:
  backend:
    # ... 其他配置
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

## 4. 手动部署

### 4.1 后端部署

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（可选）
export MODEL_CACHE_DIR="$HOME/.cache/vllm-manager/models"
export DATABASE_URL="sqlite:///./vllm_manager.db"

# 5. 启动服务
python main.py

# 后端运行在 http://localhost:8000
```

### 4.2 前端部署

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 开发模式启动
npm run dev

# 或构建生产版本
npm run build

# 4. 生产环境可使用 nginx 托管 dist 目录
```

### 4.3 使用 PM2 管理进程

```bash
# 安装 PM2
npm install -g pm2

# 后端进程配置 (ecosystem.config.js)
module.exports = {
  apps: [
    {
      name: 'vllm-manager-backend',
      cwd: './backend',
      script: 'main.py',
      interpreter: 'python3',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      env: {
        NODE_ENV: 'production',
        PORT: 8000
      }
    },
    {
      name: 'vllm-manager-frontend',
      cwd: './frontend',
      script: 'serve',
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    }
  ]
};

# 启动
pm2 start ecosystem.config.js

# 保存配置
pm2 save
pm2 startup
```

## 5. 生产环境部署

### 5.1 使用 Nginx 反向代理

```nginx
# /etc/nginx/sites-available/vllm-manager
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 5.2 HTTPS 配置

```bash
# 使用 Certbot 获取 SSL 证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 5.3 系统服务配置

创建 `/etc/systemd/system/vllm-manager.service`:

```ini
[Unit]
Description=vLLM Manager Backend
After=network.target

[Service]
Type=simple
User=vllm
WorkingDirectory=/opt/vllm_manager/backend
Environment="PATH=/opt/vllm_manager/backend/venv/bin"
Environment="MODEL_CACHE_DIR=/opt/vllm_manager/model_cache"
ExecStart=/opt/vllm_manager/backend/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable vllm-manager
sudo systemctl start vllm-manager
sudo systemctl status vllm-manager
```

## 6. 一键打包脚本

### 6.1 构建脚本 (`scripts/build.sh`)

```bash
#!/bin/bash

set -e

echo "🚀 开始构建 vLLM Manager..."

# 获取版本号
VERSION=${1:-"latest"}
echo "📦 版本: $VERSION"

# 清理旧构建
echo "🧹 清理旧构建..."
rm -rf dist/
mkdir -p dist

# 构建前端
echo "🔨 构建前端..."
cd frontend
npm ci
npm run build
cd ..
cp -r frontend/dist dist/frontend

# 构建后端
echo "🔨 构建后端..."
cd backend
pip install -r requirements.txt -t ../dist/backend/packages
cd ..
cp -r backend/*.py backend/*.txt dist/backend/
cp -r backend/model_cache dist/backend/ 2>/dev/null || true

# 复制 Docker 配置
echo "🐳 复制 Docker 配置..."
cp docker-compose.yml dist/
cp -r docker dist/

# 复制文档
echo "📚 复制文档..."
cp -r docs dist/

# 创建启动脚本
cat > dist/start.sh << 'EOF'
#!/bin/bash
docker-compose up -d
echo "✅ vLLM Manager 已启动"
echo "前端: http://localhost:3000"
echo "后端: http://localhost:8000"
EOF
chmod +x dist/start.sh

cat > dist/stop.sh << 'EOF'
#!/bin/bash
docker-compose down
echo "🛑 vLLM Manager 已停止"
EOF
chmod +x dist/stop.sh

# 打包
echo "📦 打包..."
tar -czf "vllm-manager-${VERSION}.tar.gz" -C dist .

echo "✅ 构建完成: vllm-manager-${VERSION}.tar.gz"
```

### 6.2 部署脚本 (`scripts/deploy.sh`)

```bash
#!/bin/bash

set -e

REMOTE_HOST=${1:-"user@your-server.com"}
REMOTE_DIR=${2:-"/opt/vllm_manager"}
VERSION=${3:-"latest"}

echo "🚀 部署 vLLM Manager 到 $REMOTE_HOST..."

# 上传文件
echo "📤 上传文件..."
scp "vllm-ui-${VERSION}.tar.gz" "$REMOTE_HOST:/tmp/"

# 远程执行部署
ssh "$REMOTE_HOST" << EOF
    set -e
    
    echo "🧹 清理旧版本..."
    sudo systemctl stop vllm-ui 2>/dev/null || true
    sudo rm -rf $REMOTE_DIR
    sudo mkdir -p $REMOTE_DIR
    
    echo "📦 解压..."
    sudo tar -xzf /tmp/vllm-ui-${VERSION}.tar.gz -C $REMOTE_DIR
    
    echo "🔧 配置权限..."
    sudo chown -R vllm:vllm $REMOTE_DIR
    
    echo "🐳 启动服务..."
    cd $REMOTE_DIR
    sudo docker-compose up -d
    
    echo "✅ 部署完成!"
    echo "前端: http://\$(hostname -I | awk '{print \$1}'):3000"
    echo "后端: http://\$(hostname -I | awk '{print \$1}'):8000"
EOF

echo "🎉 部署成功!"
```

## 7. 环境变量配置

### 7.1 后端环境变量

#### 基础配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MODEL_CACHE_DIR` | `~/.cache/vllm-manager/models` | 模型缓存目录 |
| `DATABASE_URL` | `None` | 完整的数据库连接 URL（优先级最高） |
| `VLLM_PORT_RANGE_START` | `8001` | vLLM 实例端口起始 |
| `VLLM_PORT_RANGE_END` | `8100` | vLLM 实例端口结束 |
| `HOST` | `0.0.0.0` | 监听地址 |
| `PORT` | `8000` | 监听端口 |
| `SECRET_KEY` | `your-secret-key` | JWT 密钥 |
| `METRICS_ENABLED` | `true` | 是否启用监控 |

#### 数据库配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DB_TYPE` | `sqlite` | 数据库类型：`sqlite`、`mysql`、`postgresql` |

**SQLite 配置（默认）：**

无需额外配置，使用本地文件存储。

**MySQL 配置：**

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MYSQL_HOST` | `localhost` | MySQL 主机地址 |
| `MYSQL_PORT` | `3306` | MySQL 端口 |
| `MYSQL_USER` | `root` | MySQL 用户名 |
| `MYSQL_PASSWORD` | `` | MySQL 密码 |
| `MYSQL_DATABASE` | `vllm_manager` | MySQL 数据库名 |
| `MYSQL_CHARSET` | `utf8mb4` | 字符集 |
| `MYSQL_POOL_SIZE` | `10` | 连接池大小 |
| `MYSQL_MAX_OVERFLOW` | `20` | 最大溢出连接数 |
| `MYSQL_POOL_TIMEOUT` | `30` | 连接池超时时间（秒） |
| `MYSQL_POOL_RECYCLE` | `3600` | 连接回收时间（秒） |

**PostgreSQL 配置（预留）：**

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `POSTGRES_HOST` | `localhost` | PostgreSQL 主机地址 |
| `POSTGRES_PORT` | `5432` | PostgreSQL 端口 |
| `POSTGRES_USER` | `postgres` | PostgreSQL 用户名 |
| `POSTGRES_PASSWORD` | `` | PostgreSQL 密码 |
| `POSTGRES_DATABASE` | `vllm_manager` | PostgreSQL 数据库名 |

#### 数据库配置示例

**方式1：使用 SQLite（默认，适合开发测试）**

```bash
# 无需配置，或显式指定
DB_TYPE=sqlite
```

**方式2：使用 MySQL（推荐生产环境）**

```bash
# 安装依赖
pip install pymysql

# 方式2.1：使用独立配置项
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=vllm_user
MYSQL_PASSWORD=your_secure_password
MYSQL_DATABASE=vllm_manager
MYSQL_CHARSET=utf8mb4

# 方式2.2：使用完整 URL（优先级更高）
DATABASE_URL=mysql+pymysql://vllm_user:your_secure_password@localhost:3306/vllm_manager?charset=utf8mb4
```

**方式3：使用 PostgreSQL**

```bash
# 安装依赖
pip install psycopg2-binary

# 使用独立配置项
DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=vllm_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DATABASE=vllm_manager
```

### 7.2 前端环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | 后端 API 地址 |
| `VITE_WS_BASE_URL` | `ws://localhost:8000` | WebSocket 地址 |

## 8. 常见问题

### 8.1 模型下载失败

```bash
# 检查磁盘空间
df -h

# 检查网络连接
curl -I https://www.modelscope.cn

# 查看日志
docker logs vllm-manager-backend
```

### 8.2 vLLM 启动失败

```bash
# 检查 GPU 驱动
nvidia-smi

# 检查端口占用
lsof -i :8001-8100

# 查看 vLLM 日志
docker exec vllm-manager-backend cat /app/model_cache/*/vllm.log
```

### 8.3 前端无法连接后端

```bash
# 检查后端状态
curl http://localhost:8000/health

# 检查 CORS 配置
grep -r "CORS" backend/

# 查看网络配置
docker network inspect vllm-network
```

## 9. 备份与恢复

### 9.1 备份

```bash
# 备份数据库和模型
tar -czf backup-$(date +%Y%m%d).tar.gz \
    backend/vllm_manager.db \
    backend/model_cache/
```

### 9.2 恢复

```bash
# 停止服务
docker-compose down

# 恢复数据
tar -xzf backup-20240101.tar.gz

# 启动服务
docker-compose up -d
```

## 10. 监控与日志

### 10.1 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 10.2 性能监控

```bash
# 查看资源使用
docker stats

# 查看 GPU 使用
watch -n 1 nvidia-smi
```

## 11. 更新升级

```bash
# 拉取最新代码
git pull origin main

# 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 数据库迁移（如有需要）
docker exec vllm-manager-backend python -c "from models import init_db; init_db()"
```
