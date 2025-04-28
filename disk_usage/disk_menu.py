import collections
import curses
import os
from typing import List

import _curses

from disk_usage.dir_scanner import Scanner
from disk_usage.formatter import Formatter
from disk_usage.shared_models import DirEntry, FileEntry, SortFilter


class DiskMenu:
    """
    Основное меню для просмотра папок на диске
    Позволяет сортировать содержимое, передвигаться от папки к папке и высчитывать размер файлов
    """

    def __init__(self, stdscr: _curses.window, path: str):

        self._directory = DirEntry(path=path, size=0, file_amount=0, files=self._get_file_entries_from_dir(path))

        self._stdscr = stdscr
        self._top_idx = 0
        self._selected_idx = 0
        self._scanner = Scanner(self._draw_bar)

        self._setup_curses()
        self._stack = collections.deque[DirEntry]()
        self._title = path
        self._sort_filter = SortFilter.BY_EXTENSION
        self._formatter = Formatter()

    def _setup_curses(self) -> None:
        """Настраивает curses"""
        curses.curs_set(0)  # Скрыть курсор
        curses.use_default_colors()
        self._stdscr.keypad(True)  # Включить обработку специальных клавиш
        self._update_window_size()

    def _update_window_size(self) -> None:
        """Обновляет размер окна"""
        self.screen_height, self.screen_width = self._stdscr.getmaxyx()
        self.visible_rows = self.screen_height - 3

    def _draw(self) -> None:
        """Перерисовывает окно"""
        self._stdscr.clear()

        self._stdscr.addstr(0, 0, self._formatter.get_title(self._title, self.screen_width), curses.A_BOLD)
        self._stdscr.addstr(self.screen_height - 1, 0, self._formatter.get_list_hint(self._sort_filter))
        self._stdscr.addstr(1, 0, self._formatter.get_legend())
        self._title = self._directory.path

        for index in range(self.visible_rows):
            item_idx = self._top_idx + index
            if item_idx >= len(self._directory.files):
                break

            prefix = "> " if item_idx == self._selected_idx else "  "
            item_text = prefix + self._formatter.entry_to_str(self._directory, item_idx)
            attr = curses.A_REVERSE if item_idx == self._selected_idx else curses.A_NORMAL
            self._stdscr.addstr(index + 2, 0, item_text[: self.screen_width - 1], attr)

        self._stdscr.refresh()

    def _handle_input(self) -> bool:
        """
        Принимает ввод:
        U - для сканирования размера файлов
        S - для сортировки файлов
        C - для выбора сортировки
        Q - выход
        При вводе соответствующему выходу из меню, подает False
        """

        try:
            key = self._stdscr.getch()

            if key == curses.KEY_UP:
                self._move_selection(-1)
            elif key == curses.KEY_DOWN:
                self._move_selection(1)
            elif key == curses.KEY_PPAGE:
                self._move_selection(-self.visible_rows)
            elif key == curses.KEY_HOME:
                self._move_selection(-9999)
            elif key == curses.KEY_END:
                self._move_selection(9999)
            elif key == curses.KEY_NPAGE:
                self._move_selection(self.visible_rows)
            elif key == ord("u"):
                self._scan()
            elif key == ord("s"):
                self._sort()
            elif key == ord("c"):
                self._change_sort()
            elif key == 10:  # Enter
                self._select_file()
            elif key == ord('q') or key == ord('й'):
                return self._back_dir()
            return True
        except Exception:
            return True

    def _move_selection(self, delta: int) -> None:
        """Двигает список в зависимости от выбранного элемента"""

        new_idx = max(0, min(self._selected_idx + delta, len(self._directory.files) - 1))
        if new_idx != self._selected_idx:
            self._selected_idx = new_idx

            if self._selected_idx < self._top_idx:
                self._top_idx = self._selected_idx

            elif self._selected_idx >= self._top_idx + self.visible_rows:
                self._top_idx = self._selected_idx - self.visible_rows + 1

    def _select_file(self) -> None:
        """Переходит по выбранной папке, если это не папка, просто выписывает это в title"""

        if self._directory.files[self._selected_idx].is_dir:
            path = self._directory.path + "/" + self._directory.files[self._selected_idx].name
            self._next_dir(path)

            if self._directory.path != path:
                self._stack.pop()
        else:
            self._title = "Передвигаться можно только по папкам"

    def _next_dir(self, path: str) -> None:
        """Проходит в следующую папку, сохраняя текущую в стек. Ничего не происходит, если такой папки нет"""
        self._stack.append(self._directory)

        self._directory = DirEntry(path=path, size=0, file_amount=0, files=self._get_file_entries_from_dir(path))

        self._top_idx = 0
        self._selected_idx = 0

        self._title = path

    def _back_dir(self) -> bool:
        self._top_idx = 0
        self._selected_idx = 0

        if len(self._stack):
            self._directory = self._stack.pop()
            self._title = self._directory.path
            return True
        else:
            return False

    def _change_sort(self) -> None:
        """Меняет текущий self.sort_filter чередованием"""
        if self._sort_filter == SortFilter.BY_EXTENSION:
            self._sort_filter = SortFilter.BY_MODIFIED
        elif self._sort_filter == SortFilter.BY_MODIFIED:
            self._sort_filter = SortFilter.BY_SIZE
        elif self._sort_filter == SortFilter.BY_SIZE:
            self._sort_filter = SortFilter.BY_COUNT
        elif self._sort_filter == SortFilter.BY_COUNT:
            self._sort_filter = SortFilter.BY_EXTENSION

    def _sort(self) -> None:
        """Сортирует файлы в текущей директории в зависимости от текущего фильтра self.sort_filter"""
        if self._sort_filter == SortFilter.BY_EXTENSION:
            self._directory.files = sorted(self._directory.files, key=lambda x: os.path.splitext(x.name)[1])
        elif self._sort_filter == SortFilter.BY_MODIFIED:
            self._directory.files = sorted(self._directory.files, key=lambda x: x.modified)
        elif self._sort_filter == SortFilter.BY_SIZE:
            self._directory.files = sorted(self._directory.files, key=lambda x: -x.size)
        elif self._sort_filter == SortFilter.BY_COUNT:
            self._directory.files = sorted(
                self._directory.files,
                key=lambda x: -self._scanner.get_files_amount(self._directory.path + "/" + x.name),
            )

    def _scan(self) -> None:
        """Находит размер всех файлов в текущей директории с помощью self.scanner, создавая прогресс бар"""
        self._stdscr.addstr(1, 0, "Начальный подсчет...")
        self._stdscr.refresh()

        if self._directory.file_amount == 0:
            self._directory.file_amount = self._scanner.get_files_amount(self._directory.path)

        total_files = self._directory.file_amount

        self._scanner.start_calculation(total_files, self._directory.files, self._directory.path)

        if not self._directory.size:
            for f in self._directory.files:
                self._directory.size += f.size

    def _draw_bar(self, progress: float) -> None:
        """Создает прогресс бар, зарисованный на progress * 100 %"""
        bar_width = self.screen_width // 4 - 4
        filled = int(progress * bar_width)

        progress_bar = "[" + "#" * filled + " " * (bar_width - filled) + "] " + str(int(progress * 100)) + " %"
        self._stdscr.addstr(1, 0, progress_bar)
        self._stdscr.refresh()

    def _get_file_entries_from_dir(self, path: str) -> List[FileEntry]:
        """Возвращает список FileEntry, лежащий по поданному path"""
        return [
            FileEntry(
                name=f,
                size=0,
                modified=int(os.path.getmtime(path + "/" + f)),
                is_dir=os.path.isdir(path + "/" + f),
            )
            for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f)) | os.path.isdir(os.path.join(path, f))
            and not os.path.islink(os.path.join(path, f))
        ]

    def go_to(self) -> None:
        """Запускает окно"""
        while True:
            self._update_window_size()
            self._draw()
            if not self._handle_input():
                break
