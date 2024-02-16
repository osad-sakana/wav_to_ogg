# WAV to OGG Converter

このプロジェクトは、WAV形式のオーディオファイルをOGG形式に変換し、処理済みのオーディオファイルを指定されたディレクトリに移動させるDockerコンテナを提供します。

## 前提条件

このプロジェクトを使用するには、Dockerがインストールされている必要があります。

## セットアップ方法

1. このリポジトリをクローンまたはダウンロードします。
2. `input` ディレクトリに変換したいWAVファイルを配置します。

## 使用方法

プロジェクトディレクトリで以下のコマンドを実行して、Dockerコンテナをビルドし、起動します。

```bash
docker-compose up --build
```

コンテナが起動すると、自動的に`input`ディレクトリ内のファイルを処理し始めます。処理が完了すると、変換されたOGGファイルが`output`ディレクトリに、元のWAVファイルが`processed`ディレクトリに移動されます。

## プロジェクト構成

- `Dockerfile`: Dockerイメージのビルドに使用されるファイルです。
- `docker-compose.yml`: Dockerコンテナの設定を定義するファイルです。
- `requirements.txt`: 必要なPythonパッケージをリストアップするファイルです。
- `app.py`: WAVファイルをOGGに変換し、指定されたディレクトリにファイルを移動させるスクリプトです。