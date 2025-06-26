"""オーディオ変換機能"""

import logging
from pathlib import Path
from typing import List, Optional

from pydub import AudioSegment


class AudioConverter:
    """WAVからOGG形式へのオーディオファイル変換を処理する"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def convert_file(
        self, input_path: Path, output_path: Optional[Path] = None
    ) -> bool:
        """
        単一のWAVファイルをOGG形式に変換する

        Args:
            input_path: 入力WAVファイルのパス
            output_path: 出力OGGファイルのパス（オプション）

        Returns:
            bool: 変換成功時はTrue、そうでなければFalse
        """
        try:
            if output_path is None:
                output_path = input_path.with_suffix(".ogg")

            self.logger.info(f"変換中: {input_path}")

            # オーディオファイルの読み込みと変換
            audio = AudioSegment.from_file(str(input_path))
            audio.export(str(output_path), format="ogg")

            self.logger.info(f"変換完了: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"{input_path}の変換エラー: {e}")
            return False

    def convert_directory(self, input_dir: Path, recursive: bool = False) -> List[Path]:
        """
        ディレクトリ内のすべてのWAVファイルをOGG形式に変換する

        Args:
            input_dir: WAVファイルを含むディレクトリ
            recursive: サブディレクトリも処理するかどうか（デフォルト: False）

        Returns:
            List[Path]: 正常に変換されたファイルのリスト
        """
        converted_files: List[Path] = []

        if not input_dir.exists() or not input_dir.is_dir():
            self.logger.error(f"ディレクトリが存在しません: {input_dir}")
            return converted_files

        # ファイル検索のパターンを取得
        pattern = "**/*.wav" if recursive else "*.wav"

        for wav_file in input_dir.glob(pattern):
            if wav_file.is_file():
                output_file = wav_file.with_suffix(".ogg")
                if self.convert_file(wav_file, output_file):
                    converted_files.append(output_file)

        return converted_files

    def is_audio_file(self, file_path: Path) -> bool:
        """
        ファイル拡張子に基づいてオーディオファイルかどうかを確認する

        Args:
            file_path: 確認するパス

        Returns:
            bool: オーディオファイル拡張子を持つ場合はTrue
        """
        audio_extensions = {".wav", ".mp3", ".flac", ".aac", ".m4a", ".ogg"}
        return file_path.suffix.lower() in audio_extensions
