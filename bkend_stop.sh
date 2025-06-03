#!/bin/bash

# 設定變數 (請根據實際路徑調整)
BASE_DIR="/home/omni/Cert_POC"
PID_FILE="$BASE_DIR/logs/fastapi.pid"
LOG_FILE="$BASE_DIR/logs/fastapi.log"
PORT="8000"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 停止服務
stop_service() {
    log "嘗試停止 FastAPI 服務..."

    # 方法1: 使用 PID 檔案
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            log "找到 PID: $PID，正在停止服務..."
            kill "$PID"
            sleep 2
            if kill -0 "$PID" 2>/dev/null; then
                warning "服務未正常停止，強制終止..."
                kill -9 "$PID"
            fi
            rm -f "$PID_FILE"
            success "服務已停止"
        else
            warning "PID 檔案中的程序已不存在"
            rm -f "$PID_FILE"
        fi
    else
        warning "找不到 PID 檔案"
    fi

    # 方法2: 使用程序名稱和端口
    log "檢查端口 $PORT 上的程序..."
    if lsof -i :$PORT > /dev/null 2>&1; then
        warning "端口 $PORT 仍有程序在運行，嘗試停止..."
        pkill -f "fastapi.*$PORT"
        sleep 2
        if lsof -i :$PORT > /dev/null 2>&1; then
            error "無法停止端口 $PORT 上的程序"
            return 1
        fi
    fi

    success "所有相關程序已停止"
}

# 清理檔案
cleanup() {
    log "清理相關檔案..."

    if [ -f "$LOG_FILE" ]; then
        log "保留日誌檔案: $LOG_FILE"
    fi

    if [ -f "$PID_FILE" ]; then
        rm -f "$PID_FILE"
        log "已刪除 PID 檔案"
    fi
}

# 主函數
main() {
    log "開始停止 FastAPI 後端服務..."

    stop_service
    cleanup

    success "服務停止完成！"
}

# 執行主函數
main

