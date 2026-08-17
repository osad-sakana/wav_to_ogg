"""GUIのTkinterビュー（ウィジェット構築とイベント配線のみ、ロジックは持たない）"""

import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Iterable, List, Optional

from tkinterdnd2 import DND_FILES, TkinterDnD

from ..converter import AudioConverter
from .dnd import paths_from_tokens
from .events import ConversionFinished
from .model import FileQueue
from .presenter import summarize_events
from .service import ConversionService

logger = logging.getLogger(__name__)

_POLL_INTERVAL_MS = 100
_MAX_FAILED_PATHS_SHOWN = 10


class WavToOggApp:
    """WAVファイルをドラッグ&ドロップしOGGへ変換するGUIアプリケーション"""

    def __init__(self, root: TkinterDnD.Tk) -> None:
        self._root = root
        self._queue = FileQueue()
        self._service: Optional[ConversionService] = None
        self._failed_paths: List[Path] = []

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
        # メソッドを追加するため、型スタブが存在せずmypyでは検出できない。
        # rootに登録することで、子ウィジェット（ラベルやボタン領域）上への
        # ドロップも受け付ける。
        root.drop_target_register(DND_FILES)
        root.dnd_bind("<<Drop>>", self._on_drop)

        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        service = self._service
        if service is not None and service.is_running():
            if not messagebox.askyesno(
                "WAV to OGG",
                "変換処理中です。現在処理中のファイルの完了を待って終了します。" "終了しますか？",
            ):
                return
            service.stop()
            self._set_controls_enabled(False)
            self._status_var.set("終了処理中...")
            self._root.after(_POLL_INTERVAL_MS, self._wait_for_shutdown)
            return
        self._root.destroy()

    def _wait_for_shutdown(self) -> None:
        service = self._service
        if service is not None and service.is_running():
            self._root.after(_POLL_INTERVAL_MS, self._wait_for_shutdown)
            return
        self._root.destroy()

    def _on_drop(self, event: Any) -> None:
        # トークンへの分割（波括弧・バックスラッシュエスケープを含むTclリスト
        # 構文の解釈）はTkの`splitlist`に委ねる
        tokens = self._root.tk.splitlist(event.data)
        self._add_paths(paths_from_tokens(tokens))

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

        self._failed_paths = []
        self._set_controls_enabled(False)
        self._status_var.set("変換中...")

        self._service = ConversionService(AudioConverter())
        self._service.start(list(self._queue.paths))
        self._root.after(_POLL_INTERVAL_MS, self._poll_service)

    def _poll_service(self) -> None:
        service = self._service
        if service is None:
            return

        summary = summarize_events(service.poll_events())
        self._failed_paths.extend(summary.failed_paths)

        if summary.finished is not None:
            self._on_conversion_finished(summary.finished)
            return

        self._root.after(_POLL_INTERVAL_MS, self._poll_service)

    def _on_conversion_finished(self, finished: ConversionFinished) -> None:
        self._status_var.set(
            f"完了: 成功 {finished.converted_count}件 / 失敗 {finished.failed_count}件"
        )
        self._set_controls_enabled(True)
        self._service = None

        if self._failed_paths:
            shown = self._failed_paths[:_MAX_FAILED_PATHS_SHOWN]
            message = "\n".join(str(path) for path in shown)
            if len(self._failed_paths) > _MAX_FAILED_PATHS_SHOWN:
                message += f"\n...他{len(self._failed_paths) - _MAX_FAILED_PATHS_SHOWN}件"
            messagebox.showwarning("WAV to OGG", f"以下のファイルの変換に失敗しました:\n\n{message}")

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
