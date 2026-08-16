"""変換待ちファイル一覧の不変な状態（tkinter非依存の純粋ロジック）"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Tuple


@dataclass(frozen=True)
class FileQueue:
    """変換待ちファイルの一覧を保持する不変な状態"""

    paths: Tuple[Path, ...] = field(default_factory=tuple)

    def add(self, candidates: Iterable[Path]) -> "FileQueue":
        """
        WAVファイルのみを重複排除して追加した新しいFileQueueを返す

        ディレクトリが渡された場合は直下（非再帰）の`.wav`ファイルへ展開する。

        Args:
            candidates: 追加候補のパス（ファイルまたはディレクトリ）

        Returns:
            FileQueue: 追加後の新しいインスタンス
        """
        merged = list(self.paths)
        for path in _expand_wav_files(candidates):
            if path not in merged:
                merged.append(path)
        return FileQueue(tuple(merged))

    def remove(self, path: Path) -> "FileQueue":
        """指定したパスを除いた新しいFileQueueを返す"""
        return FileQueue(tuple(p for p in self.paths if p != path))

    def clear(self) -> "FileQueue":
        """空の新しいFileQueueを返す"""
        return FileQueue()


def _expand_wav_files(candidates: Iterable[Path]) -> Tuple[Path, ...]:
    """ディレクトリを直下のWAVファイルへ展開し、`.wav`以外を除外する"""
    expanded = []
    for candidate in candidates:
        if candidate.is_dir():
            expanded.extend(sorted(candidate.glob("*.wav")))
        elif candidate.suffix.lower() == ".wav":
            expanded.append(candidate)
    return tuple(expanded)
