"""GUIアプリケーションのスモークテスト（表示可能な環境でのみ実行）"""

import pytest

pytest.importorskip("tkinterdnd2")

from tkinterdnd2 import TkinterDnD  # noqa: E402

from wav_to_ogg.gui.app import WavToOggApp  # noqa: E402


@pytest.mark.gui
def test_app_builds_without_error() -> None:
    try:
        root = TkinterDnD.Tk()
    except Exception:
        pytest.skip("表示可能なTkinter環境がありません")

    try:
        app = WavToOggApp(root)
        root.update_idletasks()
        assert app._queue.paths == ()
    finally:
        root.destroy()
