import os
from pydub import AudioSegment
from shutil import move

input_dir = './input'
output_dir = './output'
processed_dir = './processed'

# ディレクトリがなければ作成
for dir in [output_dir, processed_dir]:
  if not os.path.exists(dir):
    os.makedirs(dir)

# inputディレクトリ内のファイルを処理
for filename in os.listdir(input_dir):
  file_path = os.path.join(input_dir, filename)
  try:
    print(f"処理中: {filename}")
    # オーディオファイルを読み込み
    audio = AudioSegment.from_file(file_path)
    output_file_path = os.path.join(output_dir, filename.rsplit('.', 1)[0] + '.ogg')
    # ogg形式で保存
    audio.export(output_file_path, format='ogg')
    # 元のファイルをprocessedディレクトリに移動
    move(file_path, os.path.join(processed_dir, filename))
  except Exception as e:
    print(f"Error processing {filename}: {e}")
    # オーディオファイルでない場合、そのままにする
    continue

print("Processing complete.")
