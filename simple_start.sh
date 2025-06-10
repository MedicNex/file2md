#!/bin/bash
cd /www/wwwroot/medicnex-file2md
source venv/bin/activate
export API_KEY=${API_KEY:-"sk-sfncynyftubpujczaokfwiopimnmtxwxgnzmbwanwuavdhoc"}
export PORT=${PORT:-8999}
# ImageMagick环境变量
export MAGICK_HOME=/opt/homebrew/opt/imagemagick
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
