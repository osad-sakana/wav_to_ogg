"""バックグラウンドスレッドでの変換処理（tkinter非依存）"""

import logging
import queue
import threading
from pathlib import Path
from typing import List, Optional, Tuple

from ..converter import AudioConverter
from .events import ConversionEvent, ConversionFinished, FileConverted, FileFailed

logger = logging.getLogger(__name__)


class ConversionService:
    """AudioConverterをワーカースレッドで駆動し、進捗イベントをキューへ流す"""

    def __init__(self, converter: AudioConverter) -> None:
        self._converter = converter
        self._events: "queue.Queue[ConversionEvent]" = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._stop_requested = False

    def start(self, paths: List[Path]) -> None:
        """
        指定したWAVファイル群の変換をバックグラウンドスレッドで開始する

        Args:
            paths: 変換対象のWAVファイルパスの一覧
        """
        self._thread = threading.Thread(
            target=self._run, args=(tuple(paths),), daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        """
        未着手のファイルの処理を中止するよう要求する

        すでに変換が始まっているファイルは中断せず最後まで完了させる
        （中断すると出力が不完全な`.ogg`ファイルとして残るため）。
        """
        self._stop_requested = True

    def is_running(self) -> bool:
        """ワーカースレッドが実行中かどうかを返す"""
        return self._thread is not None and self._thread.is_alive()

    def poll_events(self) -> List[ConversionEvent]:
        """
        これまでに発生したイベントを取り出す

        呼び出し元スレッド（通常はTkinterのメインスレッド）から呼び出すこと。

        Returns:
            List[ConversionEvent]: 前回のポーリング以降に発生したイベント
        """
        events: List[ConversionEvent] = []
        while True:
            try:
                events.append(self._events.get_nowait())
            except queue.Empty:
                break
        return events

    def _run(self, paths: Tuple[Path, ...]) -> None:
        converted_count = 0
        failed_count = 0
        try:
            for path in paths:
                if self._stop_requested:
                    break
                if self._convert_one(path):
                    converted_count += 1
                else:
                    failed_count += 1
        finally:
            # convert_fileが想定外の例外を送出した場合でも、GUIをハングさせない
            # ようConversionFinishedを必ず発行する
            self._events.put(ConversionFinished(converted_count, failed_count))

    def _convert_one(self, path: Path) -> bool:
        try:
            output_path = path.with_suffix(".ogg")
            if self._converter.convert_file(path, output_path):
                self._events.put(FileConverted(path, output_path))
                return True
            self._events.put(FileFailed(path))
            return False
        except Exception:
            logger.exception(f"変換中に予期しないエラーが発生しました: {path}")
            self._events.put(FileFailed(path))
            return False
