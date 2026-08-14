"""wav_to_ogg.cli の結合テスト"""

import logging
import os
from pathlib import Path
from typing import Callable, Iterator, List
from unittest.mock import MagicMock, patch

import pytest

from wav_to_ogg.cli import create_parser, main


@pytest.fixture(autouse=True)
def reset_root_logger() -> Iterator[None]:
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level
    root.handlers = []
    yield
    root.handlers = original_handlers
    root.level = original_level


@pytest.fixture
def run_cli(monkeypatch: pytest.MonkeyPatch) -> Callable[[List[str]], int]:
    def _run_cli(args: List[str]) -> int:
        monkeypatch.setattr("sys.argv", ["wav-to-ogg", *args])
        return main()

    return _run_cli


class TestCreateParser:
    def test_version_flag_exits_zero(self, capsys: pytest.CaptureFixture) -> None:
        parser = create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])

        assert exc_info.value.code == 0
        assert "0.1.0" in capsys.readouterr().out

    def test_help_flag_exits_zero(self) -> None:
        parser = create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--help"])

        assert exc_info.value.code == 0

    def test_missing_input_argument_exits_nonzero(self) -> None:
        parser = create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args([])

        assert exc_info.value.code != 0

    def test_recursive_flag_defaults_to_false(self) -> None:
        parser = create_parser()

        args = parser.parse_args(["input.wav"])

        assert args.recursive is False


class TestMainSingleFile:
    def test_successful_conversion_returns_zero(
        self, run_cli: Callable[[List[str]], int], tmp_path: Path
    ) -> None:
        input_path = tmp_path / "audio.wav"
        input_path.write_bytes(b"data")

        with patch("wav_to_ogg.cli.AudioConverter") as mock_converter_cls:
            mock_converter = MagicMock()
            mock_converter.is_audio_file.return_value = True
            mock_converter.convert_file.return_value = True
            mock_converter_cls.return_value = mock_converter

            exit_code = run_cli([str(input_path)])

        assert exit_code == 0
        mock_converter.convert_file.assert_called_once_with(input_path, None)

    def test_non_audio_file_returns_one(
        self, run_cli: Callable[[List[str]], int], tmp_path: Path
    ) -> None:
        input_path = tmp_path / "notes.txt"
        input_path.write_bytes(b"data")

        with patch("wav_to_ogg.cli.AudioConverter") as mock_converter_cls:
            mock_converter = MagicMock()
            mock_converter.is_audio_file.return_value = False
            mock_converter_cls.return_value = mock_converter

            exit_code = run_cli([str(input_path)])

        assert exit_code == 1

    def test_conversion_failure_returns_one(
        self, run_cli: Callable[[List[str]], int], tmp_path: Path
    ) -> None:
        input_path = tmp_path / "audio.wav"
        input_path.write_bytes(b"data")

        with patch("wav_to_ogg.cli.AudioConverter") as mock_converter_cls:
            mock_converter = MagicMock()
            mock_converter.is_audio_file.return_value = True
            mock_converter.convert_file.return_value = False
            mock_converter_cls.return_value = mock_converter

            exit_code = run_cli([str(input_path)])

        assert exit_code == 1

    def test_explicit_output_path_is_forwarded(
        self, run_cli: Callable[[List[str]], int], tmp_path: Path
    ) -> None:
        input_path = tmp_path / "audio.wav"
        input_path.write_bytes(b"data")
        output_path = tmp_path / "out.ogg"

        with patch("wav_to_ogg.cli.AudioConverter") as mock_converter_cls:
            mock_converter = MagicMock()
            mock_converter.is_audio_file.return_value = True
            mock_converter.convert_file.return_value = True
            mock_converter_cls.return_value = mock_converter

            exit_code = run_cli([str(input_path), "-o", str(output_path)])

        assert exit_code == 0
        mock_converter.convert_file.assert_called_once_with(input_path, output_path)


class TestMainDirectory:
    def test_directory_with_dir_output_succeeds(
        self, run_cli: Callable[[List[str]], int], tmp_path: Path
    ) -> None:
        input_dir = tmp_path / "audio"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("wav_to_ogg.cli.AudioConverter") as mock_converter_cls:
            mock_converter = MagicMock()
            mock_converter.convert_directory.return_value = [
                input_dir / "a.ogg",
                input_dir / "b.ogg",
            ]
            mock_converter_cls.return_value = mock_converter

            exit_code = run_cli([str(input_dir), "-o", str(output_dir)])

        assert exit_code == 0

    def test_directory_input_with_file_output_returns_one(
        self, run_cli: Callable[[List[str]], int], tmp_path: Path
    ) -> None:
        input_dir = tmp_path / "audio"
        input_dir.mkdir()
        output_file = tmp_path / "out.ogg"
        output_file.write_bytes(b"data")

        with patch("wav_to_ogg.cli.AudioConverter"):
            exit_code = run_cli([str(input_dir), "-o", str(output_file)])

        assert exit_code == 1

    def test_no_wav_files_found_returns_zero(
        self, run_cli: Callable[[List[str]], int], tmp_path: Path
    ) -> None:
        input_dir = tmp_path / "audio"
        input_dir.mkdir()

        with patch("wav_to_ogg.cli.AudioConverter") as mock_converter_cls:
            mock_converter = MagicMock()
            mock_converter.convert_directory.return_value = []
            mock_converter_cls.return_value = mock_converter

            exit_code = run_cli([str(input_dir)])

        assert exit_code == 0

    def test_recursive_flag_is_passed_through(
        self, run_cli: Callable[[List[str]], int], tmp_path: Path
    ) -> None:
        input_dir = tmp_path / "audio"
        input_dir.mkdir()

        with patch("wav_to_ogg.cli.AudioConverter") as mock_converter_cls:
            mock_converter = MagicMock()
            mock_converter.convert_directory.return_value = [input_dir / "a.ogg"]
            mock_converter_cls.return_value = mock_converter

            run_cli(["--recursive", str(input_dir)])

        mock_converter.convert_directory.assert_called_once_with(input_dir, True)


class TestMainErrorHandling:
    def test_nonexistent_input_returns_one(
        self, run_cli: Callable[[List[str]], int]
    ) -> None:
        exit_code = run_cli(["/nonexistent/path/audio.wav"])

        assert exit_code == 1

    def test_unexpected_exception_returns_one(
        self, run_cli: Callable[[List[str]], int], tmp_path: Path
    ) -> None:
        input_path = tmp_path / "audio.wav"
        input_path.write_bytes(b"data")

        with patch("wav_to_ogg.cli.AudioConverter") as mock_converter_cls:
            mock_converter_cls.side_effect = RuntimeError("boom")

            exit_code = run_cli([str(input_path)])

        assert exit_code == 1

    def test_keyboard_interrupt_returns_130(
        self, run_cli: Callable[[List[str]], int], tmp_path: Path
    ) -> None:
        input_path = tmp_path / "audio.wav"
        input_path.write_bytes(b"data")

        with patch("wav_to_ogg.cli.AudioConverter") as mock_converter_cls:
            mock_converter_cls.side_effect = KeyboardInterrupt()

            exit_code = run_cli([str(input_path)])

        assert exit_code == 130

    def test_empty_input_path_returns_one(
        self, run_cli: Callable[[List[str]], int]
    ) -> None:
        exit_code = run_cli([""])

        assert exit_code == 1

    def test_path_neither_file_nor_directory_returns_one(
        self, run_cli: Callable[[List[str]], int], tmp_path: Path
    ) -> None:
        fifo_path = tmp_path / "pipe"
        os.mkfifo(fifo_path)

        exit_code = run_cli([str(fifo_path)])

        assert exit_code == 1

    def test_verbose_unexpected_exception_logs_traceback(
        self,
        run_cli: Callable[[List[str]], int],
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        input_path = tmp_path / "audio.wav"
        input_path.write_bytes(b"data")

        with patch("wav_to_ogg.cli.AudioConverter") as mock_converter_cls:
            mock_converter_cls.side_effect = RuntimeError("boom")

            with caplog.at_level(logging.DEBUG):
                exit_code = run_cli(["-v", str(input_path)])

        assert exit_code == 1
        assert "詳細エラー情報" in caplog.text
