"""wav_to_ogg.utils のユニットテスト"""

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from wav_to_ogg.utils import (
    ensure_directory_exists,
    get_file_size,
    setup_logging,
    validate_input_path,
)


class TestValidateInputPath:
    def test_existing_file_returns_resolved_path(self, tmp_path: Path) -> None:
        file_path = tmp_path / "audio.wav"
        file_path.write_bytes(b"data")

        result = validate_input_path(str(file_path))

        assert result == file_path.resolve()

    def test_existing_directory_returns_resolved_path(self, tmp_path: Path) -> None:
        result = validate_input_path(str(tmp_path))

        assert result == tmp_path.resolve()

    def test_nonexistent_path_raises_file_not_found_error(self, tmp_path: Path) -> None:
        missing = tmp_path / "does_not_exist.wav"

        with pytest.raises(FileNotFoundError):
            validate_input_path(str(missing))

    def test_empty_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            validate_input_path("")

    def test_relative_path_is_resolved_to_absolute(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (tmp_path / "audio.wav").write_bytes(b"data")
        monkeypatch.chdir(tmp_path)

        result = validate_input_path("audio.wav")

        assert result.is_absolute()
        assert result == (tmp_path / "audio.wav").resolve()


class TestEnsureDirectoryExists:
    def test_creates_missing_directory(self, tmp_path: Path) -> None:
        target = tmp_path / "output"

        result = ensure_directory_exists(target)

        assert result == target
        assert target.is_dir()

    def test_does_not_raise_when_directory_already_exists(self, tmp_path: Path) -> None:
        target = tmp_path / "output"
        target.mkdir()

        result = ensure_directory_exists(target)

        assert result == target
        assert target.is_dir()

    def test_creates_nested_missing_parents(self, tmp_path: Path) -> None:
        target = tmp_path / "a" / "b" / "c"

        result = ensure_directory_exists(target)

        assert result == target
        assert target.is_dir()

    def test_accepts_string_path(self, tmp_path: Path) -> None:
        target = tmp_path / "output"

        result = ensure_directory_exists(str(target))

        assert isinstance(result, Path)
        assert target.is_dir()


class TestGetFileSize:
    def test_bytes_range(self, tmp_path: Path) -> None:
        file_path = tmp_path / "f.bin"
        file_path.write_bytes(b"x" * 500)

        assert get_file_size(file_path) == "500.0 B"

    def test_kilobytes_boundary(self, tmp_path: Path) -> None:
        file_path = tmp_path / "f.bin"
        file_path.write_bytes(b"x" * 1024)

        assert get_file_size(file_path) == "1.0 KB"

    def test_megabytes_boundary(self, tmp_path: Path) -> None:
        file_path = tmp_path / "f.bin"
        file_path.write_bytes(b"x" * (1024 * 1024))

        assert get_file_size(file_path) == "1.0 MB"

    def test_nonexistent_file_returns_unknown(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.bin"

        assert get_file_size(missing) == "Unknown"


class TestSetupLogging:
    """pytest自身のログキャプチャがroot loggerにハンドラーを追加するため、
    logging.basicConfigの呼び出し引数を検証する（root loggerの実際の
    状態を見るとpytestのハンドラーによりbasicConfigがno-opになる）。"""

    def test_verbose_requests_debug_level(self) -> None:
        with patch("wav_to_ogg.utils.logging.basicConfig") as mock_basic_config:
            setup_logging(verbose=True)

        assert mock_basic_config.call_args.kwargs["level"] == logging.DEBUG

    def test_non_verbose_requests_info_level(self) -> None:
        with patch("wav_to_ogg.utils.logging.basicConfig") as mock_basic_config:
            setup_logging(verbose=False)

        assert mock_basic_config.call_args.kwargs["level"] == logging.INFO
