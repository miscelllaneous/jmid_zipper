import pytest
import tempfile
import os
import shutil
import zipfile
from pathlib import Path
from zipper import process_directories


class TestZipper:

    @pytest.fixture
    def setup_test_directories(self):
        """テスト用のディレクトリ構造を作成"""
        temp_source = tempfile.mkdtemp(prefix="test_source_")
        temp_target = tempfile.mkdtemp(prefix="test_target_")

        # サブディレクトリを作成
        subdirs = []
        for i in range(3):
            subdir = Path(temp_source) / f"subdir_{i}"
            subdir.mkdir()

            # 各サブディレクトリにテストファイルを作成
            for j in range(2):
                test_file = subdir / f"file_{j}.txt"
                test_file.write_text(f"Test content {i}-{j}")

            subdirs.append(subdir)

        yield temp_source, temp_target, subdirs

        # クリーンアップ
        if os.path.exists(temp_source):
            shutil.rmtree(temp_source)
        if os.path.exists(temp_target):
            shutil.rmtree(temp_target)

    def test_process_directories_creates_zip_files(self, setup_test_directories):
        """各サブディレクトリが正しくzipファイルとして作成されることを確認"""
        source_dir, target_dir, subdirs = setup_test_directories

        # 処理を実行
        success_count, failed_dirs = process_directories(source_dir, target_dir)

        # 成功数の確認
        assert success_count == len(subdirs), f"Expected {len(subdirs)} successful, got {success_count}"
        assert failed_dirs == [], f"Unexpected failed directories: {failed_dirs}"

        # 各サブディレクトリに対応するzipファイルが作成されているか確認
        for subdir in subdirs:
            zip_name = f"{subdir.name}.zip"
            zip_path = Path(target_dir) / zip_name
            assert zip_path.exists(), f"Zip file {zip_name} was not created"

            # zipファイルの内容を確認
            with zipfile.ZipFile(zip_path, 'r') as zf:
                namelist = zf.namelist()
                assert len(namelist) == 2, f"Expected 2 files in zip, got {len(namelist)}"

                # ファイル名の確認
                for i in range(2):
                    expected_name = f"file_{i}.txt"
                    assert any(expected_name in name for name in namelist), \
                        f"File {expected_name} not found in zip"

    def test_process_directories_deletes_source(self, setup_test_directories):
        """処理後にソースディレクトリが削除されることを確認"""
        source_dir, target_dir, subdirs = setup_test_directories

        # 処理を実行
        success_count, failed_dirs = process_directories(source_dir, target_dir)

        # 成功を確認
        assert success_count == len(subdirs)
        assert failed_dirs == []

        # 各サブディレクトリが削除されているか確認
        for subdir in subdirs:
            assert not subdir.exists(), f"Subdirectory {subdir} was not deleted"

        # ソースディレクトリが削除されているか確認
        assert not os.path.exists(source_dir), "Source directory was not deleted"

    def test_process_directories_with_empty_subdirs(self):
        """空のサブディレクトリがある場合の処理を確認"""
        temp_source = tempfile.mkdtemp(prefix="test_empty_source_")
        temp_target = tempfile.mkdtemp(prefix="test_empty_target_")

        try:
            # 空のサブディレクトリを作成
            empty_subdir = Path(temp_source) / "empty_dir"
            empty_subdir.mkdir()

            # 処理を実行
            success_count, failed_dirs = process_directories(temp_source, temp_target)

            # 成功を確認
            assert success_count == 1
            assert failed_dirs == []

            # 空のディレクトリのzipファイルも作成されることを確認
            zip_path = Path(temp_target) / "empty_dir.zip"
            assert zip_path.exists(), "Zip file for empty directory was not created"

            # サブディレクトリが削除されているか確認
            assert not empty_subdir.exists(), "Empty subdirectory was not deleted"

            # ソースディレクトリが削除されているか確認
            assert not os.path.exists(temp_source), "Source directory was not deleted"

        finally:
            # クリーンアップ
            if os.path.exists(temp_source):
                shutil.rmtree(temp_source)
            if os.path.exists(temp_target):
                shutil.rmtree(temp_target)

    def test_process_directories_invalid_source(self):
        """存在しないソースディレクトリを指定した場合にエラーが発生することを確認"""
        non_existent = "/path/that/does/not/exist"
        temp_target = tempfile.mkdtemp(prefix="test_invalid_")

        try:
            with pytest.raises(FileNotFoundError):
                process_directories(non_existent, temp_target)
        finally:
            if os.path.exists(temp_target):
                shutil.rmtree(temp_target)

    def test_process_directories_partial_failure(self):
        """一部のディレクトリの処理に失敗した場合の動作を確認"""
        temp_source = tempfile.mkdtemp(prefix="test_partial_failure_")
        temp_target = tempfile.mkdtemp(prefix="test_target_")

        try:
            # 正常なサブディレクトリを作成
            normal_subdir = Path(temp_source) / "normal_dir"
            normal_subdir.mkdir()
            (normal_subdir / "file.txt").write_text("content")

            # もう一つの正常なサブディレクトリ
            another_subdir = Path(temp_source) / "another_dir"
            another_subdir.mkdir()
            (another_subdir / "data.txt").write_text("data")

            # 処理を実行
            success_count, failed_dirs = process_directories(temp_source, temp_target)

            # 両方成功することを確認
            assert success_count == 2
            assert failed_dirs == []

            # zipファイルが作成されていることを確認
            assert (Path(temp_target) / "normal_dir.zip").exists()
            assert (Path(temp_target) / "another_dir.zip").exists()

            # サブディレクトリが削除されていることを確認
            assert not normal_subdir.exists()
            assert not another_subdir.exists()

            # ソースディレクトリも削除されていることを確認
            assert not os.path.exists(temp_source)

        finally:
            # クリーンアップ
            if os.path.exists(temp_source):
                shutil.rmtree(temp_source)
            if os.path.exists(temp_target):
                shutil.rmtree(temp_target)

    def test_process_directories_creates_target_if_not_exists(self):
        """ターゲットディレクトリが存在しない場合に自動作成されることを確認"""
        temp_source = tempfile.mkdtemp(prefix="test_source_")
        temp_target = os.path.join(tempfile.gettempdir(), "non_existent_target_dir")

        try:
            # サブディレクトリを作成
            subdir = Path(temp_source) / "test_subdir"
            subdir.mkdir()
            (subdir / "test.txt").write_text("test content")

            # 処理を実行
            success_count, failed_dirs = process_directories(temp_source, temp_target)

            # 成功を確認
            assert success_count == 1
            assert failed_dirs == []

            # ターゲットディレクトリが作成されていることを確認
            assert os.path.exists(temp_target), "Target directory was not created"

            # zipファイルが作成されていることを確認
            zip_path = Path(temp_target) / "test_subdir.zip"
            assert zip_path.exists(), "Zip file was not created"

            # サブディレクトリが削除されていることを確認
            assert not subdir.exists(), "Subdirectory was not deleted"

        finally:
            # クリーンアップ
            if os.path.exists(temp_source):
                shutil.rmtree(temp_source)
            if os.path.exists(temp_target):
                shutil.rmtree(temp_target)