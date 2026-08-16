"""wav_to_ogg.gui.service の単体テスト"""

import time
from pathlib import Path
from typing import List
from unittest.mock import MagicMock

from wav_to_ogg.gui.events import ConversionFinished, FileConverted, FileFailed
from wav_to_ogg.gui.service import ConversionEvent, ConversionService


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


def test_service_uses_ogg_suffix_for_output(tmp_path: Path) -> None:
    converter = MagicMock()
    converter.convert_file.return_value = True
    service = ConversionService(converter)

    wav_path = tmp_path / "song.wav"
    service.start([wav_path])
    _wait_for_finish(service)

    called_output_path = converter.convert_file.call_args[0][1]
    assert called_output_path == wav_path.with_suffix(".ogg")
