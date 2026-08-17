"""GUIアプリケーションのエントリーポイント"""

import logging
import shutil
import sys

from ..utils import setup_logging


def main() -> int:
    """
    GUIアプリケーションを起動する

    Returns:
        int: 終了コード（0=正常終了、1=起動失敗）
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        from tkinterdnd2 import TkinterDnD
    except ImportError:
        logger.error(
            "GUIの実行にはtkinter/tkinterdnd2が必要です。"
            '`uv sync --extra gui` または `pip install -e ".[gui]"` を実行してください。'
        )
        return 1

    try:
        root = TkinterDnD.Tk()
    except Exception as e:
        logger.error(f"GUIの起動に失敗しました（Tkinterの初期化エラー）: {e}")
        return 1

    if shutil.which("ffmpeg") is None:
        message = "ffmpegが見つかりません。変換にはffmpegのインストールが必要です。"
        logger.warning(message)
        from tkinter import messagebox

        messagebox.showwarning("WAV to OGG", message)

    from .app import WavToOggApp

    WavToOggApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
