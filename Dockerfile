# Pythonイメージの使用
FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なファイルをコピー
COPY requirements.txt requirements.txt
COPY app.py app.py

# 必要なPythonパッケージのインストール
RUN pip install --no-cache-dir -r requirements.txt

# ffmpegのインストール
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# スクリプトの実行
CMD ["python", "./app.py"]
