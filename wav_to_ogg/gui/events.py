"""GUI変換処理の進捗イベント（tkinter非依存）"""

from dataclasses import dataclass
from pathlib import Path
from typing import Union


@dataclass(frozen=True)
class FileConverted:
    """1ファイルの変換が成功したことを表す"""

    path: Path
    output_path: Path


@dataclass(frozen=True)
class FileFailed:
    """1ファイルの変換が失敗したことを表す"""

    path: Path


@dataclass(frozen=True)
class ConversionFinished:
    """すべてのファイルの変換処理が終了したことを表す"""

    converted_count: int
    failed_count: int


ConversionEvent = Union[FileConverted, FileFailed, ConversionFinished]
