"""wav_to_ogg.gui.presenter の単体テスト"""

from pathlib import Path

from wav_to_ogg.gui.events import ConversionFinished, FileConverted, FileFailed
from wav_to_ogg.gui.presenter import summarize_events


def test_summarize_events_empty_list_is_not_finished() -> None:
    summary = summarize_events([])
    assert summary.failed_paths == ()
    assert summary.finished is None


def test_summarize_events_collects_failed_paths() -> None:
    events = [
        FileConverted(Path("a.wav"), Path("a.ogg")),
        FileFailed(Path("b.wav")),
        FileFailed(Path("c.wav")),
    ]
    summary = summarize_events(events)
    assert summary.failed_paths == (Path("b.wav"), Path("c.wav"))
    assert summary.finished is None


def test_summarize_events_detects_finished() -> None:
    finished_event = ConversionFinished(converted_count=2, failed_count=1)
    events = [
        FileConverted(Path("a.wav"), Path("a.ogg")),
        FileFailed(Path("b.wav")),
        finished_event,
    ]
    summary = summarize_events(events)
    assert summary.finished is finished_event
    assert summary.failed_paths == (Path("b.wav"),)
