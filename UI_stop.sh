#!/bin/bash

PID_FILE="/home/omni/Cert_POC/frontend.pid"

if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 $PID 2>/dev/null; then
    echo "停止前端服務，PID: $PID"
    kill $PID
    sleep 2
    if kill -0 $PID 2>/dev/null; then
      echo "服務未停止，強制終止..."
      kill -9 $PID
    fi
    rm -f "$PID_FILE"
    echo "前端服務已停止"
  else
    echo "PID $PID 對應的程序不存在，刪除 PID 檔案"
    rm -f "$PID_FILE"
  fi
else
  echo "找不到 PID 檔案，無前端服務正在運行"
fi

