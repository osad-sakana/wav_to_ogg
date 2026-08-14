"""pytest共通フィクスチャ"""

import wave
from pathlib import Path
from typing import Callable

import pytest


@pytest.fixture
def make_wav_file(tmp_path: Path) -> Callable[[str], Path]:
    """最小限の有効なWAVファイルをtmp_path配下に生成するファクトリを返す"""

    def _make_wav_file(filename: str = "sample.wav") -> Path:
        wav_path = tmp_path / filename
        with wave.open(str(wav_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(8000)
            wav_file.writeframes(b"\x00\x00" * 8000)
        return wav_path

    return _make_wav_file


@pytest.fixture
def wav_file(make_wav_file: Callable[[str], Path]) -> Path:
    """単一の最小限WAVファイル"""
    return make_wav_file("sample.wav")
