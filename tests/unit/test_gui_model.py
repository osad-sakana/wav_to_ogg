"""wav_to_ogg.gui.model の単体テスト"""

from pathlib import Path
from typing import Callable

from wav_to_ogg.gui.model import FileQueue


def test_add_appends_wav_file(wav_file: Path) -> None:
    result = FileQueue().add([wav_file])
    assert result.paths == (wav_file.resolve(),)


def test_add_does_not_mutate_original(wav_file: Path) -> None:
    original = FileQueue()
    original.add([wav_file])
    assert original.paths == ()


def test_add_filters_non_wav_files(tmp_path: Path) -> None:
    text_file = tmp_path / "notes.txt"
    text_file.write_text("hello")

    result = FileQueue().add([text_file])
    assert result.paths == ()


def test_add_skips_nonexistent_path(tmp_path: Path) -> None:
    result = FileQueue().add([tmp_path / "missing.wav"])
    assert result.paths == ()


def test_add_deduplicates(wav_file: Path) -> None:
    result = FileQueue().add([wav_file]).add([wav_file])
    assert result.paths == (wav_file.resolve(),)


def test_add_deduplicates_different_notation_of_same_file(
    make_wav_file: Callable[[str], Path]
) -> None:
    a = make_wav_file("a.wav")
    indirect = a.parent / ".." / a.parent.name / "a.wav"

    result = FileQueue().add([a]).add([indirect])
    assert result.paths == (a.resolve(),)


def test_add_expands_directory(
    tmp_path: Path, make_wav_file: Callable[[str], Path]
) -> None:
    make_wav_file("a.wav")
    make_wav_file("b.wav")
    (tmp_path / "ignored.txt").write_text("x")

    result = FileQueue().add([tmp_path])
    assert result.paths == (
        (tmp_path / "a.wav").resolve(),
        (tmp_path / "b.wav").resolve(),
    )


def test_add_expands_directory_case_insensitively(
    tmp_path: Path, make_wav_file: Callable[[str], Path]
) -> None:
    make_wav_file("lower.wav")
    make_wav_file("UPPER.WAV")

    result = FileQueue().add([tmp_path])
    assert result.paths == (
        (tmp_path / "UPPER.WAV").resolve(),
        (tmp_path / "lower.wav").resolve(),
    )


def test_remove_drops_matching_path(make_wav_file: Callable[[str], Path]) -> None:
    a = make_wav_file("a.wav")
    b = make_wav_file("b.wav")

    result = FileQueue().add([a, b]).remove(a.resolve())
    assert result.paths == (b.resolve(),)


def test_remove_nonexistent_path_is_a_noop(
    make_wav_file: Callable[[str], Path]
) -> None:
    a = make_wav_file("a.wav")
    other = a.parent / "does_not_exist.wav"

    result = FileQueue().add([a]).remove(other)
    assert result.paths == (a.resolve(),)


def test_clear_returns_empty_queue(wav_file: Path) -> None:
    result = FileQueue().add([wav_file]).clear()
    assert result.paths == ()
