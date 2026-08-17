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
        seen = set(merged)
        for path in _expand_wav_files(candidates):
            if path not in seen:
                merged.append(path)
                seen.add(path)
        return FileQueue(tuple(merged))

    def remove(self, path: Path) -> "FileQueue":
        """指定したパスを除いた新しいFileQueueを返す"""
        return FileQueue(tuple(p for p in self.paths if p != path))

    def clear(self) -> "FileQueue":
        """空の新しいFileQueueを返す"""
        return FileQueue()


def _expand_wav_files(candidates: Iterable[Path]) -> Tuple[Path, ...]:
    """
    存在しないパスを除外しつつ、ディレクトリを直下のWAVファイルへ展開する

    パスは`resolve()`で正規化してから判定するため、`..`を含む同一ファイルへの
    異なる表記が別エントリとして重複排除をすり抜けることを防ぐ。
    """
    expanded = []
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_dir():
            wav_files = (
                p
                for p in resolved.iterdir()
                if p.is_file() and p.suffix.lower() == ".wav"
            )
            expanded.extend(sorted(wav_files))
        elif resolved.is_file() and resolved.suffix.lower() == ".wav":
            expanded.append(resolved)
    return tuple(expanded)
