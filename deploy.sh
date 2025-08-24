#!/bin/bash

# 定义颜色输出（可选，让提示更清晰）
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 检查并选择可用的 compose 命令
if docker compose version &>/dev/null; then
    COMPOSE="docker compose"
    echo -e "${GREEN}=> 使用: docker compose${NC}"
elif command -v docker-compose &>/dev/null; then
    COMPOSE="docker-compose"
    echo -e "${GREEN}=> 使用: docker-compose${NC}"
else
    echo -e "${RED}错误: 未找到 docker compose 或 docker-compose${NC}"
    echo "请安装 Docker Compose：https://docs.docker.com/compose/"
    exit 1
fi

# 执行操作（使用选定的 COMPOSE 命令）
echo -e "${GREEN}=> 停止服务...${NC}"
$COMPOSE down

echo -e "${GREEN}=> 构建并启动服务...${NC}"
$COMPOSE up --build -d

echo -e "${GREEN}=> 当前服务状态:${NC}"
$COMPOSE ps

echo -e "${GREEN}✅ 部署完成${NC}"