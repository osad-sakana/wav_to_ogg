"""tkinterdnd2のドロップイベントペイロードをパスへ変換する純粋関数（tkinter非依存）"""

from pathlib import Path
from typing import Iterable, List


def paths_from_tokens(tokens: Iterable[str]) -> List[Path]:
    """
    分割済みのトークン列をパスのリストに変換する

    ドロップイベントのペイロードはTclのリスト形式（スペースを含むパスは
    波括弧で囲まれ、`{`や`}`を含むパスはバックスラッシュでエスケープされる）
    のため、トークンへの分割自体はTclのリストパーサ（`root.tk.splitlist()`）
    に委ねること。この関数はその結果を受け取るだけの純粋関数とする。

    Args:
        tokens: `root.tk.splitlist(event.data)`などで分割済みの文字列群

    Returns:
        List[Path]: パスのリスト
    """
    return [Path(token) for token in tokens if token]
