"""tkinterdnd2のドロップイベントペイロードを解析する純粋関数（tkinter非依存）"""

import re
from pathlib import Path
from typing import List

_TOKEN_PATTERN = re.compile(r"\{([^}]*)\}|(\S+)")


def parse_drop_payload(data: str) -> List[Path]:
    """
    tkinterdnd2のドロップイベントデータをパスのリストに変換する

    スペースを含むパスは波括弧で囲まれる（例: "{C:/a b/x.wav} /tmp/y.wav"）。

    Args:
        data: ドロップイベントの`event.data`文字列

    Returns:
        List[Path]: ドロップされたパスのリスト
    """
    paths: List[Path] = []
    for braced, bare in _TOKEN_PATTERN.findall(data):
        token = braced if braced else bare
        if token:
            paths.append(Path(token))
    return paths
