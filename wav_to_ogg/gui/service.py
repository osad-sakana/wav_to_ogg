"""バックグラウンドスレッドでの変換処理（tkinter非依存）"""

import queue
import threading
from pathlib import Path
from typing import List, Optional, Tuple, Union

from ..converter import AudioConverter
from .events import ConversionFinished, FileConverted, FileFailed

ConversionEvent = Union[FileConverted, FileFailed, ConversionFinished]


class ConversionService:
    """AudioConverterをワーカースレッドで駆動し、進捗イベントをキューへ流す"""

    def __init__(self, converter: AudioConverter) -> None:
        self._converter = converter
        self._events: "queue.Queue[ConversionEvent]" = queue.Queue()
        self._thread: Optional[threading.Thread] = None

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
        for path in paths:
            output_path = path.with_suffix(".ogg")
            if self._converter.convert_file(path, output_path):
                converted_count += 1
                self._events.put(FileConverted(path, output_path))
            else:
                failed_count += 1
                self._events.put(FileFailed(path))
        self._events.put(ConversionFinished(converted_count, failed_count))
