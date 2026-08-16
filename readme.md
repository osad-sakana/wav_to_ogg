# WAV to OGG Converter

WAVファイルをOGG形式に変換するコマンドラインツールです。単一ファイルの変換や、ディレクトリ内のすべてのWAVファイルの一括変換に対応しています。

## 機能

- 単一のWAVファイルをOGG形式に変換
- ディレクトリ内のすべてのWAVファイルを一括変換
- 再帰的なディレクトリ処理（オプション）
- 詳細なログ出力
- エラーハンドリングと例外処理
- ドラッグ&ドロップでファイルを追加できるGUI（オプション）

## インストール方法

### uv を使用する場合（推奨）

```bash
# リポジトリをクローン
git clone <repository-url>
cd wav_to_ogg

# 依存関係をインストール
uv sync

# コマンドを実行（仮想環境を自動で使用）
uv run wav-to-ogg --help
```

GUIを使う場合はオプション依存の`gui` extraを追加でインストールしてください。

```bash
uv sync --extra gui
uv run wav-to-ogg-gui
```

### pip を使用する場合

```bash
# リポジトリをクローン
git clone <repository-url>
cd wav_to_ogg

# 依存関係をインストール
pip install -r requirements.txt

# パッケージをインストール
pip install -e .
```

GUIを使う場合は代わりに `pip install -e .[gui]` を実行してください。

### システム要件

- Python 3.8.1 以上
- ffmpeg（音声ファイル処理に必要）

#### ffmpeg のインストール

**macOS:**

```bash
brew install ffmpeg
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
[FFmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロードしてインストール

## 使用方法

### 基本的な使い方

```bash
# 単一ファイルの変換
wav-to-ogg audio.wav

# ディレクトリ内のすべてのWAVファイルを変換
wav-to-ogg /path/to/audio/directory

# 詳細出力を有効にして変換
wav-to-ogg -v audio.wav

# 再帰的にディレクトリを処理
wav-to-ogg --recursive /path/to/audio/directory
```

### コマンドライン引数

- `input`: 変換するWAVファイルまたはディレクトリ（必須）
- `-o, --output`: 出力先ファイルまたはディレクトリ（オプション、デフォルト：入力と同じ場所）
- `-r, --recursive`: ディレクトリを再帰的に処理
- `-v, --verbose`: 詳細なログ出力を有効化
- `--version`: バージョン情報を表示

### 使用例

```bash
# 単一ファイルを変換（同じディレクトリにOGGファイルを作成）
wav-to-ogg music.wav

# 単一ファイルを指定の場所に変換
wav-to-ogg music.wav -o converted/music.ogg

# ディレクトリ内のすべてのWAVファイルを変換
wav-to-ogg ./audio_files/

# サブディレクトリも含めて再帰的に変換
wav-to-ogg --recursive ./audio_collection/

# 詳細ログ付きで変換
wav-to-ogg -v ./audio_files/
```

## 動作例

```bash
$ wav-to-ogg sample.wav -v
2024-01-15 10:30:45 - wav_to_ogg.converter - INFO - Converting: sample.wav
2024-01-15 10:30:46 - wav_to_ogg.converter - INFO - Converted to: sample.ogg
2024-01-15 10:30:46 - wav_to_ogg.cli - INFO - Conversion completed successfully

$ wav-to-ogg audio_directory/
2024-01-15 10:31:20 - wav_to_ogg.converter - INFO - Converting: audio_directory/track1.wav
2024-01-15 10:31:21 - wav_to_ogg.converter - INFO - Converted to: audio_directory/track1.ogg
2024-01-15 10:31:21 - wav_to_ogg.converter - INFO - Converting: audio_directory/track2.wav
2024-01-15 10:31:22 - wav_to_ogg.converter - INFO - Converted to: audio_directory/track2.ogg
2024-01-15 10:31:22 - wav_to_ogg.cli - INFO - Successfully converted 2 files
```

## GUI

ドラッグ&ドロップでWAVファイルを追加し、OGG形式に変換できるGUIアプリケーションです。

```bash
uv sync --extra gui
uv run wav-to-ogg-gui
```

- ウィンドウへファイルをドラッグ&ドロップするか、「ファイルを追加」ボタンから選択します（フォルダをドロップした場合は直下の`.wav`ファイルが追加されます）
- 「変換」ボタンでOGGへの変換を開始します（変換はバックグラウンドで実行され、UIはブロックされません）
- `tkinterdnd2`が未インストールの場合や、システムに`ffmpeg`が無い場合は起動時にエラー・警告メッセージが表示されます

### システム要件（GUI）

- `tkinter`（多くのPython配布に標準同梱。Debian/Ubuntuでは`sudo apt install python3-tk`が別途必要な場合があります）
- `tkinterdnd2`（`uv sync --extra gui` または `pip install wav-to-ogg[gui]` でインストール）

## 開発

### 開発環境のセットアップ

```bash
# uv で開発依存関係をインストール
uv sync

# コードフォーマット
uv run black wav_to_ogg/

# リント
uv run flake8 wav_to_ogg/

# テスト実行
uv run pytest
```

### プロジェクト構成

```txt
wav_to_ogg/
├── wav_to_ogg/
│   ├── __init__.py          # パッケージ初期化
│   ├── cli.py               # コマンドラインインターフェース
│   ├── converter.py         # 音声変換機能
│   ├── utils.py             # ユーティリティ関数
│   └── gui/                 # ドラッグ&ドロップGUI（オプション機能）
│       ├── __main__.py      # GUIエントリーポイント
│       ├── app.py           # Tkinterビュー
│       ├── dnd.py           # ドロップペイロード解析
│       ├── model.py         # ファイルキューの状態
│       ├── events.py        # 変換進捗イベント
│       └── service.py       # バックグラウンド変換処理
├── pyproject.toml           # プロジェクトメタデータと依存関係定義（uv管理）
├── uv.lock                  # 依存関係のロックファイル
├── requirements.txt         # pip用依存関係リスト
└── README.md                # このファイル
```
