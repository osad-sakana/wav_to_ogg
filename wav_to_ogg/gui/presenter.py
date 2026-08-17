"""ConversionServiceのイベント列をGUI表示用に要約する（tkinter非依存の純粋ロジック）"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from .events import ConversionEvent, ConversionFinished, FileFailed


@dataclass(frozen=True)
class PollSummary:
    """1回のポーリングで発生したイベントの要約"""

    failed_paths: Tuple[Path, ...] = field(default_factory=tuple)
    finished: Optional[ConversionFinished] = None


def summarize_events(events: List[ConversionEvent]) -> PollSummary:
    """
    ConversionService.poll_events()が返すイベント列を、GUI表示用に要約する

    Args:
        events: `ConversionService.poll_events()`が返すイベント列

    Returns:
        PollSummary: 失敗したファイルのパスと、完了イベント（未完了ならNone）
    """
    failed_paths = tuple(
        event.path for event in events if isinstance(event, FileFailed)
    )
    finished = next(
        (event for event in events if isinstance(event, ConversionFinished)), None
    )
    return PollSummary(failed_paths, finished)
