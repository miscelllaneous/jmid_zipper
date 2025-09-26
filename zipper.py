import os
import shutil
import zipfile
import argparse
from pathlib import Path


def process_directories(source_dir, target_dir, reverse=False):
    """
    指定されたディレクトリ内のすべてのサブディレクトリをzipファイルに圧縮し、
    指定されたターゲットディレクトリに移動後、元のディレクトリを削除する。

    各サブディレクトリは、zipファイルの作成が成功した後に個別に削除される。

    Args:
        source_dir (str): 処理対象のディレクトリパス
        target_dir (str): zipファイルの出力先ディレクトリパス

    Raises:
        FileNotFoundError: ソースディレクトリが存在しない場合
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)

    # ソースディレクトリの存在確認
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    if not source_path.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source_dir}")

    # ターゲットディレクトリが存在しない場合は作成
    target_path.mkdir(parents=True, exist_ok=True)

    # サブディレクトリのリストを取得
    subdirectories = [d for d in source_path.iterdir() if d.is_dir()]

    # 逆順にする
    if reverse:
        subdirectories.sort(reverse=True)

    # 処理結果を記録
    successful_count = 0
    failed_dirs = []

    # 各サブディレクトリを処理
    for subdir in subdirectories:
        try:
            # zipファイル名を作成
            zip_filename = f"{subdir.name}.zip"
            zip_filepath = target_path / zip_filename

            # zipファイルを作成
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # サブディレクトリ内のすべてのファイルをzipに追加
                for root, dirs, files in os.walk(subdir):
                    for file in files:
                        file_path = Path(root) / file
                        # zipファイル内での相対パスを作成
                        arcname = file_path.relative_to(subdir)
                        zipf.write(file_path, arcname)

            print(f"Created: {zip_filepath}")

            # zipファイルが正常に作成されたことを確認
            if zip_filepath.exists() and zip_filepath.stat().st_size > 0:
                # サブディレクトリを削除
                shutil.rmtree(subdir)
                print(f"Deleted: {subdir}")
                successful_count += 1
            else:
                print(f"Warning: Zip file creation may have failed for {subdir}")
                failed_dirs.append(subdir.name)

        except Exception as e:
            print(f"Error processing {subdir}: {e}")
            failed_dirs.append(subdir.name)

    # すべてのサブディレクトリが削除された場合のみ、ソースディレクトリ自体を削除
    remaining_items = list(source_path.iterdir())
    if not remaining_items:
        # 空のソースディレクトリを削除
        source_path.rmdir()
        print(f"Deleted empty source directory: {source_dir}")
    else:
        print(f"Note: Source directory {source_dir} still contains items and was not deleted")
        if failed_dirs:
            print(f"Failed to process: {', '.join(failed_dirs)}")

    # 処理結果を報告
    print(f"\n処理完了: {successful_count}/{len(subdirectories)} ディレクトリを正常に圧縮・削除しました")

    if failed_dirs:
        return successful_count, failed_dirs
    return successful_count, []


def main():
    """CLIエントリーポイント"""
    parser = argparse.ArgumentParser(
        description='ディレクトリ内のサブディレクトリをzipファイルに圧縮して移動'
    )
    parser.add_argument(
        'source_dir',
        help='処理対象のソースディレクトリ'
    )
    parser.add_argument(
        'target_dir',
        help='zipファイルの出力先ディレクトリ'
    )

    # 逆順をオプション化する
    parser.add_argument(
        '--reverse',
        action='store_true',
        help='サブディレクトリを逆順で処理する'
    )

    args = parser.parse_args()

    try:
        process_directories(args.source_dir, args.target_dir, reverse=args.reverse)
        print("処理が完了しました。")
    except FileNotFoundError as e:
        print(f"エラー: {e}")
        return 1
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())