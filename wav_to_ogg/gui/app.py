"""GUIのTkinterビュー（ウィジェット構築とイベント配線のみ、ロジックは持たない）"""

import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Iterable, Optional

from tkinterdnd2 import DND_FILES, TkinterDnD

from ..converter import AudioConverter
from .dnd import parse_drop_payload
from .events import ConversionFinished, FileConverted, FileFailed
from .model import FileQueue
from .service import ConversionService

logger = logging.getLogger(__name__)

_POLL_INTERVAL_MS = 100


class WavToOggApp:
    """WAVファイルをドラッグ&ドロップしOGGへ変換するGUIアプリケーション"""

    def __init__(self, root: TkinterDnD.Tk) -> None:
        self._root = root
        self._queue = FileQueue()
        self._service: Optional[ConversionService] = None

        root.title("WAV to OGG コンバーター")
        root.geometry("480x360")

        self._listbox = tk.Listbox(root, selectmode=tk.EXTENDED)
        self._listbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        button_frame = ttk.Frame(root)
        button_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        self._add_button = ttk.Button(
            button_frame, text="ファイルを追加", command=self._on_add_files
        )
        self._add_button.pack(side=tk.LEFT)

        self._remove_button = ttk.Button(
            button_frame, text="選択を削除", command=self._on_remove_selected
        )
        self._remove_button.pack(side=tk.LEFT, padx=(4, 0))

        self._clear_button = ttk.Button(
            button_frame, text="クリア", command=self._on_clear
        )
        self._clear_button.pack(side=tk.LEFT, padx=(4, 0))

        self._convert_button = ttk.Button(
            button_frame, text="変換", command=self._on_convert
        )
        self._convert_button.pack(side=tk.RIGHT)

        self._status_var = tk.StringVar(value="WAVファイルをここへドラッグ&ドロップしてください")
        status_label = ttk.Label(root, textvariable=self._status_var, anchor=tk.W)
        status_label.pack(fill=tk.X, padx=8, pady=(0, 8))

        # tkinterdnd2はTkinterDnD.Tk()生成時にウィジェットへ動的にこれらの
        # メソッドを追加するため、型スタブが存在せずmypyでは検出できない
        self._listbox.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
        self._listbox.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore[attr-defined]

        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        if self._service is not None:
            if not messagebox.askyesno(
                "WAV to OGG",
                "変換処理が完了していません。終了すると処理中のファイルが" "不完全な状態になる場合があります。終了しますか？",
            ):
                return
            self._service = None
        self._root.destroy()

    def _on_drop(self, event: Any) -> None:
        self._add_paths(parse_drop_payload(event.data))

    def _on_add_files(self) -> None:
        filenames = filedialog.askopenfilenames(
            title="WAVファイルを選択", filetypes=[("WAVファイル", "*.wav")]
        )
        self._add_paths(Path(name) for name in filenames)

    def _on_remove_selected(self) -> None:
        selected_paths = [
            Path(self._listbox.get(i)) for i in self._listbox.curselection()
        ]
        for path in selected_paths:
            self._queue = self._queue.remove(path)
        self._refresh_listbox()

    def _on_clear(self) -> None:
        self._queue = self._queue.clear()
        self._refresh_listbox()

    def _on_convert(self) -> None:
        if not self._queue.paths:
            messagebox.showinfo("WAV to OGG", "変換するファイルがありません")
            return

        self._set_controls_enabled(False)
        self._status_var.set("変換中...")

        self._service = ConversionService(AudioConverter())
        self._service.start(list(self._queue.paths))
        self._root.after(_POLL_INTERVAL_MS, self._poll_service)

    def _poll_service(self) -> None:
        service = self._service
        if service is None:
            return

        for event in service.poll_events():
            if isinstance(event, FileConverted):
                logger.info(f"変換完了: {event.output_path}")
            elif isinstance(event, FileFailed):
                logger.error(f"変換失敗: {event.path}")
            elif isinstance(event, ConversionFinished):
                self._status_var.set(
                    f"完了: 成功 {event.converted_count}件 / " f"失敗 {event.failed_count}件"
                )
                self._set_controls_enabled(True)
                self._service = None
                return

        self._root.after(_POLL_INTERVAL_MS, self._poll_service)

    def _add_paths(self, candidates: Iterable[Path]) -> None:
        self._queue = self._queue.add(candidates)
        self._refresh_listbox()

    def _refresh_listbox(self) -> None:
        self._listbox.delete(0, tk.END)
        for path in self._queue.paths:
            self._listbox.insert(tk.END, str(path))

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        self._add_button["state"] = state
        self._remove_button["state"] = state
        self._clear_button["state"] = state
        self._convert_button["state"] = state
