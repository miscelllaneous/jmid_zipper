# Directory Zipper Tool

ディレクトリ内の複数のサブディレクトリをそれぞれzipファイルに圧縮し、指定した場所へ移動後、元のディレクトリを削除するツールです。

## 機能

- 指定ディレクトリ内のすべてのサブディレクトリを個別のzipファイルに圧縮
- 圧縮したzipファイルを指定したディレクトリへ移動
- 処理完了後、元のソースディレクトリを自動削除
- Windows環境対応
- デフォルトディレクトリの設定機能

## インストール

### 前提条件

- Python 3.11以上
- uv (Python パッケージマネージャー)
  - インストール方法: https://docs.astral.sh/uv/

### セットアップ

```bash
# リポジトリのクローン
git clone <repository-url>
cd jmid_zipper

# uvで依存関係のインストール
uv pip install -e .
```

## 使用方法

### コマンドライン (Python直接実行)

```bash
uv run python zipper.py <ソースディレクトリ> <ターゲットディレクトリ>
```

### Windows バッチファイル

```cmd
# 引数を指定して実行
run_zipper.bat C:\source\folder C:\backup\folder

# デフォルトディレクトリを使用（設定済みの場合）
run_zipper.bat
```

### Windows PowerShell

```powershell
# 引数を指定して実行
.\run_zipper.ps1 -SourceDir "C:\source\folder" -TargetDir "C:\backup\folder"

# デフォルトディレクトリを使用（設定済みの場合）
.\run_zipper.ps1
```

## デフォルトディレクトリの設定

頻繁に同じディレクトリを使用する場合、デフォルト値を設定できます。

### 方法1: スクリプト内で直接編集

- `run_zipper.bat` の11-12行目
- `run_zipper.ps1` の3-4行目

```batch
set DEFAULT_SOURCE_DIR=C:\temp\source
set DEFAULT_TARGET_DIR=C:\temp\backup
```

### 方法2: 設定ファイルを使用（推奨）

1. サンプルファイルをコピー
```cmd
copy zipper_config.bat.sample zipper_config.bat
copy zipper_config.ps1.sample zipper_config.ps1
```

2. 設定ファイルを編集してデフォルトディレクトリを指定

設定ファイルがある場合、スクリプトが自動的に読み込みます。

## 例

```
# 元のディレクトリ構造
C:\source\
  ├── project1\
  │   ├── file1.txt
  │   └── file2.txt
  ├── project2\
  │   └── data.csv
  └── project3\
      └── config.json

# コマンド実行
run_zipper.bat C:\source C:\backup

# 実行後
C:\backup\
  ├── project1.zip
  ├── project2.zip
  └── project3.zip

# C:\source ディレクトリは削除される
```

## テスト

```bash
# テストの実行
uv run pytest test_zipper.py -v
```

## 注意事項

- ソースディレクトリは処理後に**完全に削除**されます
- 処理前に重要なデータのバックアップを取ることを推奨します
- ターゲットディレクトリが存在しない場合は自動的に作成されます
- デフォルトディレクトリを使用する場合でも、引数で指定すれば上書きできます