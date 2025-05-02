import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from disk_usage.dir_scanner import Scanner
from disk_usage.shared_models import FileEntry


class TestScanner:
    @pytest.fixture
    def scanner(self) -> Scanner:
        draw_bar_mock = MagicMock()
        return Scanner(draw_bar_mock)

    def test_scanner_calculate_size(self, tmp_path: Path, scanner: Scanner) -> None:
        file1 = tmp_path / "file1.txt"
        file1.write_text("test" * 1000)

        file2 = tmp_path / "file2.txt"
        file2.write_text("test" * 7700)

        subdir = tmp_path / "subdir"
        subdir.mkdir()

        file3 = subdir / "file3.txt"
        file3.write_text("test" * 80)

        files = [
            FileEntry(name="file1.txt", modified=0, size=0, is_dir=False),
            FileEntry(name="file2.txt", modified=0, size=0, is_dir=False),
            FileEntry(name="subdir", modified=0, size=0, is_dir=True),
        ]

        scanner.start_calculation(3, files, tmp_path)

        assert files[0].size == os.path.getsize(file1)
        assert files[1].size == os.path.getsize(file2)
        assert files[2].size >= os.path.getsize(file3)

    def test_get_files_amount_empty_dir(self, tmp_path: Path, scanner: Scanner) -> None:
        assert scanner.get_files_amount(str(tmp_path)) == 0

    def test_get_files_amount_with_files(self, tmp_path: Path, scanner: Scanner) -> None:
        for i in range(3):
            (tmp_path / f"file_{i}.txt").write_text("test")

        assert scanner.get_files_amount(str(tmp_path)) == 3

    def test_get_files_amount_with_subdirs(self, tmp_path: Path, scanner: Scanner) -> None:
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "file2.txt").write_text("test")

        subdir = tmp_path / "subdir"
        subdir.mkdir()

        for i in range(3):
            (subdir / f"subfile_{i}.txt").write_text("test")

        assert scanner.get_files_amount(str(tmp_path)) == 5
