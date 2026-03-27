#!/bin/bash

set -e

# 参数
REMOTE_HOST=${1:-""}
REMOTE_DIR=${2:-"/opt/vllm_manager"}
VERSION=${3:-"latest"}

if [ -z "$REMOTE_HOST" ]; then
    echo "❌ 错误: 请指定远程主机"
    echo "用法: $0 <user@host> [远程目录] [版本号]"
    echo "示例: $0 root@192.168.1.100 /opt/vllm_manager latest"
    exit 1
fi

echo "🚀 部署 vLLM Manager 到 $REMOTE_HOST..."
echo "📂 远程目录: $REMOTE_DIR"
echo "📦 版本: $VERSION"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 检查构建包是否存在
PACKAGE_FILE="$PROJECT_DIR/vllm-manager-${VERSION}.tar.gz"
if [ ! -f "$PACKAGE_FILE" ]; then
    echo "❌ 错误: 构建包不存在: $PACKAGE_FILE"
    echo "请先运行: ./scripts/build.sh $VERSION"
    exit 1
fi

# 上传文件
echo "📤 上传文件到远程服务器..."
scp "$PACKAGE_FILE" "$REMOTE_HOST:/tmp/"

# 远程执行部署
ssh "$REMOTE_HOST" << EOF
    set -e
    
    echo "🧹 清理旧版本..."
    sudo mkdir -p $REMOTE_DIR
    sudo rm -rf $REMOTE_DIR/*
    
    echo "📦 解压..."
    sudo tar -xzf /tmp/vllm-ui-${VERSION}.tar.gz -C $REMOTE_DIR
    
    echo "🔧 配置权限..."
    sudo chmod +x $REMOTE_DIR/*.sh
    
    echo "🐳 启动服务..."
    cd $REMOTE_DIR
    sudo docker-compose down 2>/dev/null || true
    sudo docker-compose up -d
    
    echo ""
    echo "✅ 部署完成!"
    echo ""
    echo "访问地址:"
    echo "  前端: http://\$(curl -s ifconfig.me):3000"
    echo "  后端: http://\$(curl -s ifconfig.me):8000"
    echo ""
    echo "管理命令:"
    echo "  cd $REMOTE_DIR"
    echo "  ./stop.sh    - 停止服务"
    echo "  ./start.sh   - 启动服务"
    echo "  ./status.sh  - 查看状态"
    echo "  ./logs.sh    - 查看日志"
EOF

echo ""
echo "🎉 部署成功!"
echo ""
echo "请访问: http://$REMOTE_HOST:3000"
