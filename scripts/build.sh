#!/bin/bash

set -e

echo "🚀 开始构建 vLLM Manager..."

# 获取版本号
VERSION=${1:-"latest"}
echo "📦 版本: $VERSION"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# 清理旧构建
echo "🧹 清理旧构建..."
rm -rf dist/
mkdir -p dist

# 构建前端
echo "🔨 构建前端..."
cd "$PROJECT_DIR/frontend"
npm ci
npm run build

# 创建前端 Docker 构建目录
mkdir -p "$PROJECT_DIR/dist/frontend"
cp -r "$PROJECT_DIR/frontend/dist"/* "$PROJECT_DIR/dist/frontend/" 2>/dev/null || true
cp "$PROJECT_DIR/frontend/package.json" "$PROJECT_DIR/dist/frontend/"
cp "$PROJECT_DIR/frontend/package-lock.json" "$PROJECT_DIR/dist/frontend/" 2>/dev/null || true

# 创建后端构建目录
echo "🔨 准备后端..."
mkdir -p "$PROJECT_DIR/dist/backend"
cp -r "$PROJECT_DIR/backend"/*.py "$PROJECT_DIR/backend/requirements.txt" "$PROJECT_DIR/dist/backend/"

# 复制 Docker 配置
echo "🐳 复制 Docker 配置..."
cp "$PROJECT_DIR/docker-compose.yml" "$PROJECT_DIR/dist/"
cp -r "$PROJECT_DIR/backend/Dockerfile" "$PROJECT_DIR/dist/backend/"

# 复制文档
echo "📚 复制文档..."
cp -r "$PROJECT_DIR/docs" "$PROJECT_DIR/dist/" 2>/dev/null || true

# 创建启动脚本
cat > "$PROJECT_DIR/dist/start.sh" << 'EOF'
#!/bin/bash
echo "🚀 启动 vLLM UI..."
docker-compose up -d
echo ""
echo "✅ vLLM UI 已启动"
echo "前端: http://localhost:3000"
echo "后端: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
EOF
chmod +x "$PROJECT_DIR/dist/start.sh"

cat > "$PROJECT_DIR/dist/stop.sh" << 'EOF'
#!/bin/bash
echo "🛑 停止 vLLM UI..."
docker-compose down
echo "✅ vLLM UI 已停止"
EOF
chmod +x "$PROJECT_DIR/dist/stop.sh"

cat > "$PROJECT_DIR/dist/status.sh" << 'EOF'
#!/bin/bash
docker-compose ps
EOF
chmod +x "$PROJECT_DIR/dist/status.sh"

cat > "$PROJECT_DIR/dist/logs.sh" << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "查看所有服务日志..."
    docker-compose logs -f
else
    echo "查看 $1 日志..."
    docker-compose logs -f "$1"
fi
EOF
chmod +x "$PROJECT_DIR/dist/logs.sh"

# 打包
echo "📦 打包..."
cd "$PROJECT_DIR"
tar -czf "vllm-ui-${VERSION}.tar.gz" -C dist .

echo ""
echo "✅ 构建完成: vllm-ui-${VERSION}.tar.gz"
echo ""
echo "使用方式:"
echo "  1. 解压: tar -xzf vllm-ui-${VERSION}.tar.gz"
echo "  2. 启动: ./start.sh"
echo "  3. 停止: ./stop.sh"
echo "  4. 查看状态: ./status.sh"
echo "  5. 查看日志: ./logs.sh [backend|frontend]"
