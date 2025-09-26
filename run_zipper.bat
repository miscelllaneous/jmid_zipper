@echo off
setlocal EnableDelayedExpansion

echo ===============================================
echo Directory Zipper Tool
echo ===============================================
echo.

REM デフォルトディレクトリの設定（必要に応じて変更してください）
REM =====================================
set DEFAULT_SOURCE_DIR=C:\temp\source
set DEFAULT_TARGET_DIR=C:\temp\backup
REM =====================================

REM 設定ファイルがあれば読み込む
if exist "zipper_config.bat" (
    call zipper_config.bat
    echo 設定ファイルを読み込みました: zipper_config.bat
    echo.
)

REM 引数処理とデフォルト値の適用
if "%~1"=="" (
    if defined DEFAULT_SOURCE_DIR (
        set SOURCE_DIR=%DEFAULT_SOURCE_DIR%
        echo デフォルトのソースディレクトリを使用します: %DEFAULT_SOURCE_DIR%
    ) else (
        echo エラー: ソースディレクトリを指定してください
        echo.
        echo 使用方法: %~n0 [ソースディレクトリ] [ターゲットディレクトリ]
        echo.
        echo 例: %~n0 C:\source\folder C:\backup\folder
        echo.
        echo デフォルト値を設定するには、zipper_config.batファイルを作成するか、
        echo このファイル内のDEFAULT_SOURCE_DIRとDEFAULT_TARGET_DIRを編集してください。
        exit /b 1
    )
) else (
    set SOURCE_DIR=%~1
)

if "%~2"=="" (
    if defined DEFAULT_TARGET_DIR (
        set TARGET_DIR=%DEFAULT_TARGET_DIR%
        echo デフォルトのターゲットディレクトリを使用します: %DEFAULT_TARGET_DIR%
    ) else (
        echo エラー: ターゲットディレクトリを指定してください
        echo.
        echo 使用方法: %~n0 [ソースディレクトリ] [ターゲットディレクトリ]
        echo.
        echo 例: %~n0 C:\source\folder C:\backup\folder
        echo.
        echo デフォルト値を設定するには、zipper_config.batファイルを作成するか、
        echo このファイル内のDEFAULT_SOURCE_DIRとDEFAULT_TARGET_DIRを編集してください。
        exit /b 1
    )
) else (
    set TARGET_DIR=%~2
)

echo ソースディレクトリ: %SOURCE_DIR%
echo ターゲットディレクトリ: %TARGET_DIR%
echo.

REM uvがインストールされているか確認
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo エラー: uvが見つかりません。
    echo uvをインストールしてください: https://docs.astral.sh/uv/
    exit /b 1
)

REM Python環境の確認とセットアップ
if not exist ".venv" (
    echo 仮想環境を作成しています...
    uv venv
    if %errorlevel% neq 0 (
        echo エラー: 仮想環境の作成に失敗しました
        exit /b 1
    )
)

REM 依存関係のインストール
echo 依存関係を確認しています...
uv pip install -q -e .
if %errorlevel% neq 0 (
    echo エラー: 依存関係のインストールに失敗しました
    exit /b 1
)

echo.
echo 処理を開始します...
echo ===============================================

REM メインスクリプトの実行
uv run python zipper.py "%SOURCE_DIR%" "%TARGET_DIR%"

if %errorlevel% equ 0 (
    echo.
    echo ===============================================
    echo 処理が正常に完了しました！
    echo ===============================================
) else (
    echo.
    echo ===============================================
    echo エラーが発生しました。
    echo ===============================================
    exit /b %errorlevel%
)

endlocal