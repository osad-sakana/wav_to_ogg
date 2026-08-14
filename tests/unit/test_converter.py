"""wav_to_ogg.converter のユニットテスト"""

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
from unittest.mock import MagicMock, patch

import pytest

from wav_to_ogg.converter import AudioConverter


def _has_libvorbis_encoder() -> bool:
    """OGG変換に必要なffmpegのlibvorbisエンコーダーが利用可能か確認する"""
    if shutil.which("ffmpeg") is None:
        return False
    try:
        result = subprocess.run(
            ["ffmpeg", "-encoders"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return "libvorbis" in result.stdout


@pytest.fixture
def converter() -> AudioConverter:
    return AudioConverter()


class TestIsAudioFile:
    @pytest.mark.parametrize(
        "filename",
        ["a.wav", "a.mp3", "a.flac", "a.aac", "a.m4a", "a.ogg", "a.WAV", "a.Mp3"],
    )
    def test_recognized_extensions_return_true(
        self, converter: AudioConverter, filename: str
    ) -> None:
        assert converter.is_audio_file(Path(filename)) is True

    @pytest.mark.parametrize("filename", ["a.txt", "a.pdf", "a", "a.wav.txt"])
    def test_unrecognized_extensions_return_false(
        self, converter: AudioConverter, filename: str
    ) -> None:
        assert converter.is_audio_file(Path(filename)) is False


class TestConvertFile:
    def test_default_output_path_swaps_extension_to_ogg(
        self, converter: AudioConverter, tmp_path: Path
    ) -> None:
        input_path = tmp_path / "audio.wav"
        input_path.write_bytes(b"fake wav data")
        mock_audio = MagicMock()

        with patch(
            "wav_to_ogg.converter.AudioSegment.from_file", return_value=mock_audio
        ) as mock_from_file:
            result = converter.convert_file(input_path)

        assert result is True
        mock_from_file.assert_called_once_with(str(input_path))
        mock_audio.export.assert_called_once_with(
            str(tmp_path / "audio.ogg"), format="ogg"
        )

    def test_explicit_output_path_is_used(
        self, converter: AudioConverter, tmp_path: Path
    ) -> None:
        input_path = tmp_path / "audio.wav"
        input_path.write_bytes(b"fake wav data")
        output_path = tmp_path / "custom" / "renamed.ogg"
        mock_audio = MagicMock()

        with patch(
            "wav_to_ogg.converter.AudioSegment.from_file", return_value=mock_audio
        ):
            result = converter.convert_file(input_path, output_path)

        assert result is True
        mock_audio.export.assert_called_once_with(str(output_path), format="ogg")

    def test_returns_false_and_does_not_raise_on_decode_error(
        self, converter: AudioConverter, tmp_path: Path
    ) -> None:
        input_path = tmp_path / "broken.wav"
        input_path.write_bytes(b"not really audio")

        with patch(
            "wav_to_ogg.converter.AudioSegment.from_file",
            side_effect=RuntimeError("decode failed"),
        ):
            result = converter.convert_file(input_path)

        assert result is False

    def test_returns_false_when_export_raises(
        self, converter: AudioConverter, tmp_path: Path
    ) -> None:
        input_path = tmp_path / "audio.wav"
        input_path.write_bytes(b"fake wav data")
        mock_audio = MagicMock()
        mock_audio.export.side_effect = OSError("disk full")

        with patch(
            "wav_to_ogg.converter.AudioSegment.from_file", return_value=mock_audio
        ):
            result = converter.convert_file(input_path)

        assert result is False


class TestConvertDirectory:
    def test_nonexistent_directory_returns_empty_list(
        self, converter: AudioConverter, tmp_path: Path
    ) -> None:
        missing = tmp_path / "missing"

        assert converter.convert_directory(missing) == []

    def test_file_passed_instead_of_directory_returns_empty_list(
        self, converter: AudioConverter, tmp_path: Path
    ) -> None:
        file_path = tmp_path / "not_a_dir.wav"
        file_path.write_bytes(b"data")

        assert converter.convert_directory(file_path) == []

    def test_non_recursive_only_processes_top_level_wav_files(
        self,
        converter: AudioConverter,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (tmp_path / "top.wav").write_bytes(b"data")
        (tmp_path / "ignored.txt").write_bytes(b"data")
        nested_dir = tmp_path / "nested"
        nested_dir.mkdir()
        (nested_dir / "deep.wav").write_bytes(b"data")

        calls: List[Path] = []

        def fake_convert_file(
            input_path: Path, output_path: Optional[Path] = None
        ) -> bool:
            calls.append(input_path)
            return True

        monkeypatch.setattr(converter, "convert_file", fake_convert_file)

        result = converter.convert_directory(tmp_path, recursive=False)

        assert calls == [tmp_path / "top.wav"]
        assert result == [tmp_path / "top.ogg"]

    def test_recursive_processes_nested_wav_files(
        self,
        converter: AudioConverter,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (tmp_path / "top.wav").write_bytes(b"data")
        nested_dir = tmp_path / "nested"
        nested_dir.mkdir()
        (nested_dir / "deep.wav").write_bytes(b"data")

        monkeypatch.setattr(converter, "convert_file", lambda i, o=None: True)

        result = converter.convert_directory(tmp_path, recursive=True)

        assert sorted(result) == sorted([tmp_path / "top.ogg", nested_dir / "deep.ogg"])

    def test_continues_processing_after_individual_file_failure(
        self,
        converter: AudioConverter,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (tmp_path / "good.wav").write_bytes(b"data")
        (tmp_path / "bad.wav").write_bytes(b"data")

        def fake_convert_file(
            input_path: Path, output_path: Optional[Path] = None
        ) -> bool:
            return input_path.name != "bad.wav"

        monkeypatch.setattr(converter, "convert_file", fake_convert_file)

        result = converter.convert_directory(tmp_path, recursive=False)

        assert result == [tmp_path / "good.ogg"]


@pytest.mark.skipif(
    not _has_libvorbis_encoder(),
    reason="ffmpeg with libvorbis encoder is required for real conversion",
)
class TestConvertFileIntegration:
    def test_real_wav_to_ogg_conversion(
        self, converter: AudioConverter, wav_file: Path
    ) -> None:
        result = converter.convert_file(wav_file)

        output_path = wav_file.with_suffix(".ogg")
        assert result is True
        assert output_path.exists()
        assert output_path.stat().st_size > 0
