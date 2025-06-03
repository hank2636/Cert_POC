#!/bin/bash

LOG_FILE="/home/omni/Cert_POC/logs/frontend.log"
PID_FILE="/home/omni/Cert_POC/frontend.pid"

cd "/home/omni/Cert_POC/frontend"
nohup npm run dev > "$LOG_FILE" 2>&1 &

PID=$!
echo $PID > "$PID_FILE"

echo "前端服務已啟動，PID: $PID"
echo "日誌檔案: $LOG_FILE"

