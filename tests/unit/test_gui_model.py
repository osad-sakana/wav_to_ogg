"""wav_to_ogg.gui.model の単体テスト"""

from pathlib import Path
from typing import Callable

from wav_to_ogg.gui.model import FileQueue


def test_add_appends_wav_file(wav_file: Path) -> None:
    result = FileQueue().add([wav_file])
    assert result.paths == (wav_file,)


def test_add_does_not_mutate_original(wav_file: Path) -> None:
    original = FileQueue()
    original.add([wav_file])
    assert original.paths == ()


def test_add_filters_non_wav_files(tmp_path: Path) -> None:
    text_file = tmp_path / "notes.txt"
    text_file.write_text("hello")

    result = FileQueue().add([text_file])
    assert result.paths == ()


def test_add_deduplicates(wav_file: Path) -> None:
    result = FileQueue().add([wav_file]).add([wav_file])
    assert result.paths == (wav_file,)


def test_add_expands_directory(
    tmp_path: Path, make_wav_file: Callable[[str], Path]
) -> None:
    make_wav_file("a.wav")
    make_wav_file("b.wav")
    (tmp_path / "ignored.txt").write_text("x")

    result = FileQueue().add([tmp_path])
    assert result.paths == (tmp_path / "a.wav", tmp_path / "b.wav")


def test_remove_drops_matching_path(make_wav_file: Callable[[str], Path]) -> None:
    a = make_wav_file("a.wav")
    b = make_wav_file("b.wav")

    result = FileQueue().add([a, b]).remove(a)
    assert result.paths == (b,)


def test_clear_returns_empty_queue(wav_file: Path) -> None:
    result = FileQueue().add([wav_file]).clear()
    assert result.paths == ()
