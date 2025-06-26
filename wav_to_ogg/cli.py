"""WAVからOGGコンバーター用のコマンドラインインターフェース"""

import argparse
import logging
import sys
from pathlib import Path

from .converter import AudioConverter
from .utils import setup_logging, validate_input_path


def create_parser() -> argparse.ArgumentParser:
    """引数パーサーを作成し設定する"""
    parser = argparse.ArgumentParser(
        description="WAVオーディオファイルをOGG形式に変換",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s audio.wav                    # 単一ファイルを変換
  %(prog)s /path/to/audio/              # ディレクトリ内のすべてのWAVファイルを変換
  %(prog)s -v audio.wav                 # 詳細出力
  %(prog)s --recursive /path/to/audio/  # 再帰的に変換（サブディレクトリも含む）
        """,
    )

    parser.add_argument(
        "input", help="入力WAVファイルまたはWAVファイルを含むディレクトリ"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="出力ファイルまたはディレクトリ（デフォルト：入力と同じ場所）",
    )

    parser.add_argument(
        "-r", "--recursive", action="store_true", help="ディレクトリを再帰的に処理"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="詳細出力を有効化"
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    return parser


def main() -> int:
    """CLIアプリケーションのメインエントリーポイント"""
    parser = create_parser()
    args = parser.parse_args()

    # ログ設定
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # 入力パスを検証
        input_path = validate_input_path(args.input)
        converter = AudioConverter()

        if input_path.is_file():
            # 単一ファイル変換
            if not converter.is_audio_file(input_path):
                logger.error(f"ファイルはオーディオファイルではないようです: {input_path}")
                return 1

            output_path = None
            if args.output:
                output_path = Path(args.output)

            success = converter.convert_file(input_path, output_path)
            if not success:
                return 1

            logger.info("変換が正常に完了しました")

        elif input_path.is_dir():
            # ディレクトリ変換
            if args.output and not Path(args.output).is_dir():
                logger.error("入力がディレクトリの場合、出力もディレクトリでなければなりません")
                return 1

            converted_files = converter.convert_directory(input_path, args.recursive)

            if not converted_files:
                logger.warning("変換するWAVファイルが見つかりませんでした")
                return 0

            logger.info(f"{len(converted_files)}個のファイルを正常に変換しました")

        else:
            logger.error(f"入力パスがファイルでもディレクトリでもありません: {input_path}")
            return 1

    except FileNotFoundError as e:
        logger.error(str(e))
        return 1
    except ValueError as e:
        logger.error(str(e))
        return 1
    except KeyboardInterrupt:
        logger.info("ユーザーによって操作がキャンセルされました")
        return 130
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        if args.verbose:
            logger.exception("詳細エラー情報:")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
