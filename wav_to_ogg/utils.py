"""ファイルおよびディレクトリ操作用のユーティリティ関数"""

import logging
from pathlib import Path
from typing import Union


def setup_logging(verbose: bool = False) -> None:
    """
    アプリケーションのログ設定を行う

    Args:
        verbose: Trueの場合詳細ログを有効化
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """
    ディレクトリが存在することを確認し、必要に応じて作成する

    Args:
        path: ディレクトリのパス

    Returns:
        Path: Pathオブジェクトとしてのディレクトリパス
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(file_path: Path) -> str:
    """
    人間が読みやすいファイルサイズを取得する

    Args:
        file_path: ファイルのパス

    Returns:
        str: フォーマットされたファイルサイズ
    """
    try:
        size_bytes = file_path.stat().st_size
        size: float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except OSError:
        return "Unknown"


def validate_input_path(path_str: str) -> Path:
    """
    入力パス文字列を検証しPathオブジェクトに変換する

    Args:
        path_str: パスの文字列表現

    Returns:
        Path: 検証済みのpathオブジェクト

    Raises:
        FileNotFoundError: パスが存在しない場合
        ValueError: パスが無効な場合
    """
    if not path_str:
        raise ValueError("パスは空にできません")

    path = Path(path_str).resolve()

    if not path.exists():
        raise FileNotFoundError(f"パスが存在しません: {path}")

    return path
