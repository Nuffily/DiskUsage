import os
from functools import lru_cache
from pathlib import Path
from typing import Callable

from disk_usage.shared_models import FileEntry


class Scanner:
    """Класс помогающий вычислить размер всех файлов в DirEntry"""

    def __init__(self, draw_bar_func: Callable[[float], None]):
        """С помощью draw_bar_func будет отображаться прогресс подсчета"""
        self._progress: float = 0
        self._total_size = 0
        self._checked_count = 0
        self._skipped_count = 0
        self._draw_bar = draw_bar_func

    def _calculate_size(self, path: str, total_files: int) -> int:
        """Вычисляет размер с обновлением прогресс-бара из self.draw_bar"""
        current_size = self._total_size

        try:
            # С использованием PathLib длительность метода увеличивается раз в 10, можно с os оставить?
            with os.scandir(path) as it:
                for entry in it:
                    try:

                        if entry.is_symlink():
                            continue

                        if entry.is_file():
                            self._total_size += entry.stat().st_size
                            self._checked_count += 1
                            self._progress = self._checked_count / (total_files + 1)  # +1 чтобы избежать деления на 0

                        elif entry.is_dir():
                            self._calculate_size(entry.path, total_files)

                    except (PermissionError, FileNotFoundError):
                        self._skipped_count += 1
                    finally:
                        self._draw_bar(self._progress)

        except PermissionError:
            self._skipped_count += 1

        return self._total_size - current_size

    def start_calculation(self, total_files: int, files: list[FileEntry], path: str) -> None:
        """
        Вычисляет размер каждого файла в поданной директории и вписывает его в ячейку size файла
        Во время счета обновляет прогресс бар
        """
        self._progress = 0
        self._total_size = 0
        self._checked_count = 0
        self._skipped_count = 0

        for file in files:

            if (Path(path) / file.name).is_symlink():

                continue

            if not file.is_dir:
                file.size = (Path(path) / file.name).stat().st_size

            else:
                file.size = self._calculate_size(path + "/" + file.name, total_files)

    @lru_cache(maxsize=1024)
    def get_files_amount(self, path: str) -> int:
        """Возвращает количество файлов в директории по поданному path. Кэшируется"""
        total_files = 0
        for root, dirs, files in os.walk(path):  # То же самое, очень долго с PathLib
            try:
                total_files += len(files)
            except PermissionError:
                continue
        return total_files
