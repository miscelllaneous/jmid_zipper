# デフォルトディレクトリの設定（必要に応じて変更してください）
# =====================================
$DefaultSourceDir = "C:\temp\source"
$DefaultTargetDir = "C:\temp\backup"
# =====================================

# 設定ファイルがあれば読み込む
$configFile = ".\zipper_config.ps1"
if (Test-Path $configFile) {
    . $configFile
    Write-Host "設定ファイルを読み込みました: $configFile" -ForegroundColor Green
    Write-Host ""
}

param(
    [Parameter(Mandatory=$false, Position=0, HelpMessage="処理対象のソースディレクトリを指定してください")]
    [string]$SourceDir,

    [Parameter(Mandatory=$false, Position=1, HelpMessage="zipファイルの出力先ディレクトリを指定してください")]
    [string]$TargetDir
)

# デフォルト値の適用
if (-not $SourceDir) {
    if ($DefaultSourceDir) {
        $SourceDir = $DefaultSourceDir
        Write-Host "デフォルトのソースディレクトリを使用します: $DefaultSourceDir" -ForegroundColor Yellow
    } else {
        Write-Host "エラー: ソースディレクトリを指定してください" -ForegroundColor Red
        Write-Host ""
        Write-Host "使用方法: .\$($MyInvocation.MyCommand.Name) [ソースディレクトリ] [ターゲットディレクトリ]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "例: .\$($MyInvocation.MyCommand.Name) C:\source\folder C:\backup\folder" -ForegroundColor Gray
        Write-Host ""
        Write-Host "デフォルト値を設定するには、zipper_config.ps1ファイルを作成するか、" -ForegroundColor Gray
        Write-Host "このファイル内の`$DefaultSourceDirと`$DefaultTargetDirを編集してください。" -ForegroundColor Gray
        exit 1
    }
}

if (-not $TargetDir) {
    if ($DefaultTargetDir) {
        $TargetDir = $DefaultTargetDir
        Write-Host "デフォルトのターゲットディレクトリを使用します: $DefaultTargetDir" -ForegroundColor Yellow
    } else {
        Write-Host "エラー: ターゲットディレクトリを指定してください" -ForegroundColor Red
        Write-Host ""
        Write-Host "使用方法: .\$($MyInvocation.MyCommand.Name) [ソースディレクトリ] [ターゲットディレクトリ]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "例: .\$($MyInvocation.MyCommand.Name) C:\source\folder C:\backup\folder" -ForegroundColor Gray
        Write-Host ""
        Write-Host "デフォルト値を設定するには、zipper_config.ps1ファイルを作成するか、" -ForegroundColor Gray
        Write-Host "このファイル内の`$DefaultSourceDirと`$DefaultTargetDirを編集してください。" -ForegroundColor Gray
        exit 1
    }
}

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Directory Zipper Tool" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "ソースディレクトリ: $SourceDir" -ForegroundColor Yellow
Write-Host "ターゲットディレクトリ: $TargetDir" -ForegroundColor Yellow
Write-Host ""

# uvがインストールされているか確認
try {
    $uvVersion = uv --version 2>$null
    if (-not $uvVersion) {
        throw "uvが見つかりません"
    }
} catch {
    Write-Host "エラー: uvが見つかりません。" -ForegroundColor Red
    Write-Host "uvをインストールしてください: https://docs.astral.sh/uv/" -ForegroundColor Red
    exit 1
}

# Python環境の確認とセットアップ
if (-not (Test-Path ".venv")) {
    Write-Host "仮想環境を作成しています..." -ForegroundColor Green
    uv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "エラー: 仮想環境の作成に失敗しました" -ForegroundColor Red
        exit 1
    }
}

# 依存関係のインストール
Write-Host "依存関係を確認しています..." -ForegroundColor Green
uv pip install -q -e . 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "エラー: 依存関係のインストールに失敗しました" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "処理を開始します..." -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# メインスクリプトの実行
uv run python zipper.py $SourceDir $TargetDir

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "処理が正常に完了しました！" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Red
    Write-Host "エラーが発生しました。" -ForegroundColor Red
    Write-Host "===============================================" -ForegroundColor Red
    exit $LASTEXITCODE
}