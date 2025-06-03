#!/bin/bash

# 設定變數
BACKEND_DIR="/home/omni/Cert_POC/backend"
VENV_PATH="/home/omni/Cert_POC/.venv/bin/activate"
HOST="172.16.1.112"
PORT="8000"
APP_PATH="/home/omni/Cert_POC/backend/app/main.py"
LOG_DIR="/home/omni/Cert_POC/logs"
LOG_FILE="$LOG_DIR/fastapi.log"
PID_FILE="$LOG_DIR/fastapi.pid"

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

# 檢查是否在正確的目錄
check_directory() {
    if [ ! -d "$BACKEND_DIR" ]; then
        error "找不到 $BACKEND_DIR 目錄，請確認在正確的專案根目錄執行此腳本"
        exit 1
    fi
    log "找到 $BACKEND_DIR 目錄"
}

# 檢查虛擬環境
check_venv() {
    if [ ! -f "$VENV_PATH" ]; then
        error "找不到虛擬環境，請確認路徑：$VENV_PATH"
        exit 1
    fi
    log "找到虛擬環境"
}

# 檢查應用程式檔案
check_app() {
    if [ ! -f "$APP_PATH" ]; then
        error "找不到應用程式檔案：$APP_PATH"
        exit 1
    fi
    log "找到應用程式檔案"
}

# 檢查端口是否被佔用
check_port() {
    if lsof -i :$PORT > /dev/null 2>&1; then
        warning "端口 $PORT 已被佔用，嘗試停止現有服務..."
        pkill -f "fastapi.*$PORT" || true
        sleep 2
        if lsof -i :$PORT > /dev/null 2>&1; then
            error "無法釋放端口 $PORT，請手動停止佔用的程序"
            exit 1
        fi
    fi
    log "端口 $PORT 可用"
}

# 啟動服務
start_service() {
    log "啟動虛擬環境..."
    source "$VENV_PATH"

    # 確保日誌目錄存在
    mkdir -p "$LOG_DIR"

    log "啟動 FastAPI 服務..."
    cd $BACKEND_DIR
    nohup fastapi dev "$APP_PATH" --host "$HOST" --port "$PORT" > "$LOG_FILE" 2>&1 &
    #echo "nohup fastapi dev "$APP_PATH" --host "$HOST" --port "$PORT" > "$LOG_FILE" 2>&1 &"
    # 獲取程序 PID
    FASTAPI_PID=$!
    echo $FASTAPI_PID > "$PID_FILE"

    log "FastAPI 服務已在背景啟動"
    log "PID: $FASTAPI_PID"
    log "主機: $HOST"
    log "端口: $PORT"
    log "日誌檔案: $LOG_FILE"
    log "PID 檔案: $PID_FILE"
}

# 驗證服務啟動
verify_service() {
    local max_attempts=200
    local attempt=1
    #local chars=('⣾' '⣷' '⣯' '⣟' '⡿' '⢿' '⣻' '⣽')
    local chars=('◐' '◓' '◑' '◒')
    local spinner_index=0

    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://$HOST:$PORT" > /dev/null 2>&1; then
            echo -ne "\r"
            success "FastAPI 服務啟動成功！"
            success "訪問地址: http://$HOST:$PORT"
            success "API 文檔: http://$HOST:$PORT/docs"
            return 0
        else
            printf "\r${chars[$spinner_index]}" "$attempt"
            spinner_index=$(( (spinner_index + 1) % ${#chars[@]} ))
            sleep 0.1
            ((attempt++))
        fi
    done

    echo -ne "\r"
    error "服務啟動失敗，經過 $max_attempts 次嘗試後仍無法連線，請檢查日誌：$LOG_FILE"
    exit 1
}



# 主函數
main() {
    log "開始啟動 FastAPI 後端服務..."

    check_directory
    check_venv
    check_app
    check_port
    start_service
    verify_service

    success "腳本執行完成！"
}

# 執行主函數
main

