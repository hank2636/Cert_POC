#!/bin/bash

echo "停止前端服務 (UI_stop.sh)..."
bash UI_stop.sh

echo "停止後端服務 (bkend_stop.sh)..."
bash bkend_stop.sh

echo "停止 ngrok 服務 (ngrokk_stop.sh)..."
bash ngrok_stop.sh

echo "全部服務停止完成！"

