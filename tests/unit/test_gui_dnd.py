"""wav_to_ogg.gui.dnd の単体テスト"""

from pathlib import Path

from wav_to_ogg.gui.dnd import parse_drop_payload


def test_parse_drop_payload_single_path() -> None:
    assert parse_drop_payload("/tmp/audio.wav") == [Path("/tmp/audio.wav")]


def test_parse_drop_payload_multiple_paths() -> None:
    result = parse_drop_payload("/tmp/a.wav /tmp/b.wav")
    assert result == [Path("/tmp/a.wav"), Path("/tmp/b.wav")]


def test_parse_drop_payload_braced_path_with_spaces() -> None:
    result = parse_drop_payload("{/tmp/My Music/a.wav} /tmp/b.wav")
    assert result == [Path("/tmp/My Music/a.wav"), Path("/tmp/b.wav")]


def test_parse_drop_payload_japanese_path() -> None:
    result = parse_drop_payload("{/tmp/音楽/曲.wav}")
    assert result == [Path("/tmp/音楽/曲.wav")]


def test_parse_drop_payload_empty_string() -> None:
    assert parse_drop_payload("") == []


def test_parse_drop_payload_empty_braces_are_skipped() -> None:
    assert parse_drop_payload("{} /tmp/a.wav") == [Path("/tmp/a.wav")]
