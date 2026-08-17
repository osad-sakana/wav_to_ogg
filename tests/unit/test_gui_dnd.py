"""wav_to_ogg.gui.dnd の単体テスト"""

from pathlib import Path

from wav_to_ogg.gui.dnd import paths_from_tokens


def test_paths_from_tokens_single_path() -> None:
    assert paths_from_tokens(["/tmp/audio.wav"]) == [Path("/tmp/audio.wav")]


def test_paths_from_tokens_multiple_paths() -> None:
    result = paths_from_tokens(["/tmp/a.wav", "/tmp/b.wav"])
    assert result == [Path("/tmp/a.wav"), Path("/tmp/b.wav")]


def test_paths_from_tokens_path_with_spaces() -> None:
    result = paths_from_tokens(["/tmp/My Music/a.wav", "/tmp/b.wav"])
    assert result == [Path("/tmp/My Music/a.wav"), Path("/tmp/b.wav")]


def test_paths_from_tokens_path_with_braces() -> None:
    result = paths_from_tokens(["/tmp/we{ird}/x.wav"])
    assert result == [Path("/tmp/we{ird}/x.wav")]


def test_paths_from_tokens_japanese_path() -> None:
    result = paths_from_tokens(["/tmp/音楽/曲.wav"])
    assert result == [Path("/tmp/音楽/曲.wav")]


def test_paths_from_tokens_empty_iterable() -> None:
    assert paths_from_tokens([]) == []


def test_paths_from_tokens_skips_empty_strings() -> None:
    assert paths_from_tokens(["", "/tmp/a.wav"]) == [Path("/tmp/a.wav")]
