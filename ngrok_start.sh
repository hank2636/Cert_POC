#!/bin/bash

LOG_FILE="/home/omni/Cert_POC/logs/ngrok.log"
PID_FILE="/home/omni/Cert_POC/ngrok.pid"

# 檢查 jq 是否已安裝
if ! command -v jq > /dev/null 2>&1; then
    echo "錯誤：未安裝 jq，請先安裝 jq 後再執行本腳本"
    echo "安裝方式（Ubuntu/Debian）：sudo apt install jq"
    exit 1
fi

# 啟動 ngrok
nohup ngrok start --all > "$LOG_FILE" 2>&1 &

PID=$!
echo $PID > "$PID_FILE"

echo "ngrok 服務已啟動，PID: $PID"
echo "日誌檔案: $LOG_FILE"

# 等待 ngrok API 啟動
echo "等待 ngrok API 啟動..."
max_attempts=20
attempt=1
while [ $attempt -le $max_attempts ]; do
    if curl -s http://127.0.0.1:4040/api/tunnels > /dev/null; then
        break
    fi
    sleep 0.5
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "無法連接 ngrok API，請稍後檢查 log"
    exit 1
fi

# 取得 tunnels JSON
TUNNELS_JSON=$(curl -s http://127.0.0.1:4040/api/tunnels)

# 分析每條 tunnel 並標示
echo "目前 ngrok 公開網址："
echo "$TUNNELS_JSON" | jq -r '.tunnels[] | "\(.config.addr) \(.public_url)"' | while read -r line; do
    addr=$(echo "$line" | awk '{print $1}')
    url=$(echo "$line" | awk '{print $2}')

    if [[ "$addr" == *"8000"* ]]; then
        echo "後端 URL: $url"
    elif [[ "$addr" == *"5173"* ]]; then
        echo "前端 URL: $url"
    else
        echo "其他 URL: $url (對應本地位址: $addr)"
    fi
done

