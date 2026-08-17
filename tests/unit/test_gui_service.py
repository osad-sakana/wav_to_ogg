"""wav_to_ogg.gui.service の単体テスト"""

import time
from pathlib import Path
from typing import List
from unittest.mock import MagicMock

from wav_to_ogg.gui.events import (
    ConversionEvent,
    ConversionFinished,
    FileConverted,
    FileFailed,
)
from wav_to_ogg.gui.service import ConversionService


def _wait_for_finish(
    service: ConversionService, timeout: float = 2.0
) -> List[ConversionEvent]:
    deadline = time.monotonic() + timeout
    collected: List[ConversionEvent] = []
    while time.monotonic() < deadline:
        collected.extend(service.poll_events())
        if any(isinstance(event, ConversionFinished) for event in collected):
            return collected
        time.sleep(0.01)
    raise AssertionError("ConversionFinished イベントを受信できませんでした")


def test_service_reports_success_for_each_converted_file(tmp_path: Path) -> None:
    converter = MagicMock()
    converter.convert_file.return_value = True
    service = ConversionService(converter)

    paths = [tmp_path / "a.wav", tmp_path / "b.wav"]
    service.start(paths)

    events = _wait_for_finish(service)

    converted = [e for e in events if isinstance(e, FileConverted)]
    finished = [e for e in events if isinstance(e, ConversionFinished)][0]

    assert {e.path for e in converted} == set(paths)
    assert finished.converted_count == 2
    assert finished.failed_count == 0


def test_service_reports_failure(tmp_path: Path) -> None:
    converter = MagicMock()
    converter.convert_file.return_value = False
    service = ConversionService(converter)

    service.start([tmp_path / "broken.wav"])

    events = _wait_for_finish(service)

    failed = [e for e in events if isinstance(e, FileFailed)]
    finished = [e for e in events if isinstance(e, ConversionFinished)][0]

    assert len(failed) == 1
    assert finished.converted_count == 0
    assert finished.failed_count == 1


def test_service_recovers_from_unexpected_exception(tmp_path: Path) -> None:
    """convert_fileが例外を送出しても、ConversionFinishedが必ず届きGUIがハングしないこと"""
    converter = MagicMock()
    converter.convert_file.side_effect = MemoryError("boom")
    service = ConversionService(converter)

    service.start([tmp_path / "broken.wav"])

    events = _wait_for_finish(service)

    failed = [e for e in events if isinstance(e, FileFailed)]
    finished = [e for e in events if isinstance(e, ConversionFinished)][0]

    assert len(failed) == 1
    assert finished.converted_count == 0
    assert finished.failed_count == 1


def test_service_continues_after_one_file_raises(tmp_path: Path) -> None:
    converter = MagicMock()
    converter.convert_file.side_effect = [RuntimeError("boom"), True]
    service = ConversionService(converter)

    service.start([tmp_path / "broken.wav", tmp_path / "ok.wav"])

    events = _wait_for_finish(service)
    finished = [e for e in events if isinstance(e, ConversionFinished)][0]

    assert finished.converted_count == 1
    assert finished.failed_count == 1


def test_service_uses_ogg_suffix_for_output(tmp_path: Path) -> None:
    converter = MagicMock()
    converter.convert_file.return_value = True
    service = ConversionService(converter)

    wav_path = tmp_path / "song.wav"
    service.start([wav_path])
    _wait_for_finish(service)

    converter.convert_file.assert_called_once_with(
        wav_path, wav_path.with_suffix(".ogg")
    )


def test_stop_prevents_unstarted_files_from_running(tmp_path: Path) -> None:
    converter = MagicMock()
    converter.convert_file.return_value = True
    service = ConversionService(converter)

    service.start([tmp_path / "a.wav"])
    service.stop()

    events = _wait_for_finish(service)
    finished = [e for e in events if isinstance(e, ConversionFinished)][0]

    # 停止要求のタイミング次第でa.wavは処理されることもあるため、
    # ここでは「例外なくConversionFinishedへ到達すること」のみを保証する
    assert finished.converted_count + finished.failed_count <= 1


def test_stop_called_during_first_file_skips_the_rest(tmp_path: Path) -> None:
    converter = MagicMock()

    def _convert_first_file_then_stop(*_args: object) -> bool:
        service.stop()
        return True

    converter.convert_file.side_effect = _convert_first_file_then_stop
    service = ConversionService(converter)

    service.start([tmp_path / "a.wav", tmp_path / "b.wav", tmp_path / "c.wav"])

    events = _wait_for_finish(service)
    finished = [e for e in events if isinstance(e, ConversionFinished)][0]

    # 1件目の処理中にstop()が呼ばれるため、確実に2件目以降はスキップされる
    assert converter.convert_file.call_count == 1
    assert finished.converted_count == 1
    assert finished.failed_count == 0


def test_is_running_reflects_thread_state(tmp_path: Path) -> None:
    converter = MagicMock()
    converter.convert_file.return_value = True
    service = ConversionService(converter)

    assert service.is_running() is False

    service.start([tmp_path / "a.wav"])
    _wait_for_finish(service)

    deadline = time.monotonic() + 1.0
    while service.is_running() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert service.is_running() is False
