import os
from functools import lru_cache
from typing import Callable, List

from disk_usage.shared_models import FileEntry


class Scanner:
    """Класс помогающий вычислить размер всех файлов в DirEntry"""

    def __init__(self, draw_bar_func: Callable[[float], None]):
        """С помощью draw_bar_func будет отображаться прогресс подсчета"""
        self.progress: float = 0
        self.total_size = 0
        self.checked_count = 0
        self.skipped_count = 0
        self.draw_bar = draw_bar_func

    def _calculate_size(self, path: str, total_files: int) -> int:
        """Вычисляет размер с обновлением прогресс-бара из self.draw_bar"""
        current_size = self.total_size

        try:
            with os.scandir(path) as it:
                for entry in it:
                    try:

                        if entry.is_symlink():
                            continue

                        if entry.is_file():
                            self.total_size += entry.stat().st_size
                            self.checked_count += 1
                            self.progress = self.checked_count / (total_files + 1)  # +1 чтобы избежать деления на 0

                        elif entry.is_dir():
                            self._calculate_size(entry.path, total_files)

                    except (PermissionError, FileNotFoundError):
                        self.skipped_count += 1
                    finally:
                        self.draw_bar(self.progress)

        except PermissionError:
            self.skipped_count += 1

        return self.total_size - current_size

    def start_calculation(self, total_files: int, files: List[FileEntry], path: str) -> None:
        """
        Вычисляет размер каждого файла в поданной директории и вписывает его в ячейку size файла
        Во время счета обновляет прогресс бар
        """
        self.progress = 0
        self.total_size = 0
        self.checked_count = 0
        self.skipped_count = 0

        for i in range(len(files)):
            current = files[i]

            if os.path.islink(path + "/" + current.name):
                continue

            if not current.is_dir:
                current.size = os.path.getsize(path + "/" + current.name)

            else:
                current.size = self._calculate_size(path + "/" + current.name, total_files)

    @lru_cache(maxsize=1024)
    def get_files_amount(self, path: str) -> int:
        total_files = 0
        for root, dirs, files in os.walk(path):
            try:
                total_files += len(files)
            except PermissionError:
                continue
        return total_files
