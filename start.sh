#!/bin/bash

echo "啟動後端服務 (bkend_start.sh)..."
bash bkend_start.sh

echo "啟動前端服務 (UI_start.sh)..."
bash UI_start.sh

#echo "啟動 ngrok 服務 (ngrok_start.sh)..."
#bash ngrok_start.sh

echo "全部服務啟動完成！"

