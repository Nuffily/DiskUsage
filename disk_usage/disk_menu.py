import collections
import curses
import os
from typing import List

from formatter import Formatter
from shared_models import FileEntry, DirEntry, SortFilter
from dir_scanner import Scanner


class DiskMenu:
    def __init__(self, stdscr, path):

        self.directory = DirEntry(
            path=path,
            size=0,
            file_amount=0,
            files=self.get_file_entries_from_dir(path)
        )

        self.stdscr = stdscr
        self.top_idx = 0
        self.selected_idx = 0
        self.scanner = Scanner(self.draw_bar)

        self.setup_curses()
        self.stack = collections.deque[DirEntry]()
        self.title = path
        self.sort_filter = SortFilter.BY_EXTENSION
        self.formatter = Formatter()

    def next_dir(self, path):
        self.stack.append(self.directory)

        self.directory = DirEntry(
            path=path,
            size=0,
            file_amount=0,
            files=self.get_file_entries_from_dir(path)
        )

        self.top_idx = 0
        self.selected_idx = 0

        self.title = path

    def back_dir(self):
        self.top_idx = 0
        self.selected_idx = 0

        if len(self.stack):
            self.directory = self.stack.pop()
            self.title = self.directory.path
            return True
        else:
            return False

    def setup_curses(self):
        curses.curs_set(0)  # Скрыть курсор
        curses.use_default_colors()
        self.stdscr.keypad(True)  # Включить обработку специальных клавиш
        self.update_window_size()

    def update_window_size(self):
        self.screen_height, self.screen_width = self.stdscr.getmaxyx()
        self.visible_rows = self.screen_height - 3

    def draw(self):
        self.stdscr.clear()

        title = "-" * 4 + self.title[:self.screen_width - 1] + "-" * (
                self.screen_width - 4 - len(self.title[:self.screen_width - 1]))
        self.stdscr.addstr(0, 0, title, curses.A_BOLD)
        self.stdscr.addstr(self.screen_height - 1, 0,
                           self.formatter.get_list_hint(self.sort_filter))
        self.stdscr.addstr(1, 0,
                           self.formatter.get_legend())
        self.title = self.directory.path

        for i in range(self.visible_rows):
            item_idx = self.top_idx + i
            if item_idx >= len(self.directory.files):
                break

            prefix = "> " if item_idx == self.selected_idx else "  "
            item_text = prefix + self.formatter.entry_to_str(self.directory, item_idx)
            attr = curses.A_REVERSE if item_idx == self.selected_idx else curses.A_NORMAL
            self.stdscr.addstr(i + 2, 0, item_text[:self.screen_width - 1], attr)

        self.stdscr.refresh()

    def handle_input(self):
        """
        Принимает ввод:
        U - для сканирования размера файлов
        S - для сортировки файлов
        C - для выбора сортировки
        Q - выход
        При вводе соответствующему выходу из меню, подает False
        """

        try:
            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                self.move_selection(-1)
            elif key == curses.KEY_DOWN:
                self.move_selection(1)
            elif key == curses.KEY_PPAGE:
                self.move_selection(-self.visible_rows)
            elif key == curses.KEY_HOME:
                self.move_selection(-9999)
            elif key == curses.KEY_END:
                self.move_selection(9999)
            elif key == curses.KEY_NPAGE:
                self.move_selection(self.visible_rows)
            elif key == ord("u"):
                self.scan()
            elif key == ord("s"):
                self.sort()
            elif key == ord("c"):
                self.change_sort()
            elif key == 10:  # Enter
                self.select_file()
            elif key == ord('q') or key == ord('й'):
                return self.back_dir()
            return True
        except:
            return True

    def move_selection(self, delta):
        """Двигает список в зависимости от выбранного элемента"""

        new_idx = max(0, min(self.selected_idx + delta, len(self.directory.files) - 1))
        if new_idx != self.selected_idx:
            self.selected_idx = new_idx

            if self.selected_idx < self.top_idx:
                self.top_idx = self.selected_idx

            elif self.selected_idx >= self.top_idx + self.visible_rows:
                self.top_idx = self.selected_idx - self.visible_rows + 1

    def select_file(self):
        """Переходит по выбранной папке, если это не папка, просто выписывает это в title"""

        if self.directory.files[self.selected_idx].is_dir:
            path = self.directory.path + "/" + self.directory.files[self.selected_idx].name
            self.next_dir(path)

            if self.directory.path != path:
                self.stack.pop()
        else:
            self.title = "Передвигаться можно только по папкам"

    def go_to(self):
        """Запускает окно"""
        while True:
            self.update_window_size()
            self.draw()
            if not self.handle_input():
                break

    def change_sort(self):
        if self.sort_filter == SortFilter.BY_EXTENSION:
            self.sort_filter = SortFilter.BY_MODIFIED
        elif self.sort_filter == SortFilter.BY_MODIFIED:
            self.sort_filter = SortFilter.BY_SIZE
        elif self.sort_filter == SortFilter.BY_SIZE:
            self.sort_filter =SortFilter.BY_COUNT
        elif self.sort_filter == SortFilter.BY_COUNT:
            self.sort_filter = SortFilter.BY_EXTENSION

    def sort(self):
        if self.sort_filter == SortFilter.BY_EXTENSION:
            self.directory.files = sorted(self.directory.files, key=lambda x: os.path.splitext(x.name)[1])
        elif self.sort_filter == SortFilter.BY_MODIFIED:
            self.directory.files = sorted(self.directory.files, key=lambda x: x.modified)
        elif self.sort_filter == SortFilter.BY_SIZE:
            self.directory.files = sorted(self.directory.files, key=lambda x: -x.size)
        elif self.sort_filter == SortFilter.BY_COUNT:
            self.directory.files = (sorted(self.directory.files,
                                           key=lambda x: -self.scanner.get_files_amount(
                                               self.directory.path + "/" + x.name)))

    def scan(self):
        self.stdscr.addstr(1, 0, "Начальный подсчет...")
        self.stdscr.refresh()

        if self.directory.file_amount == 0:
            self.directory.file_amount = self.scanner.get_files_amount(self.directory.path)

        total_files = self.directory.file_amount

        self.scanner.start_calculation(total_files, self.directory.files, self.directory.path)

        if not self.directory.size:
            for f in self.directory.files:
                self.directory.size += f.size

    def draw_bar(self, progress: float) -> None:
        bar_width = self.screen_width // 4 - 4
        filled = int(progress * bar_width)

        progress_bar = "[" + "#" * filled + " " * (bar_width - filled) + "] " + str(
            int(progress * 100)) + " %"
        self.stdscr.addstr(1, 0, progress_bar)
        self.stdscr.refresh()

    def get_file_entries_from_dir(self, path: str) -> List[FileEntry]:
        return [FileEntry(
            name=f,
            size=0,
            modified=int(os.path.getmtime(path + "/" + f)),
            is_dir=os.path.isdir(path + "/" + f),
        )
            for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) | os.path.isdir(os.path.join(path, f))
                                         and not os.path.islink(os.path.join(path, f))]
# def get_kolvo(path):
#     total_files = 0
#     for root, dirs, files in os.walk(path):
#         try:
#             total_files += len(files)
#         except PermissionError:
#             continue
#     return total_files


# def to_papkas(stdscr, path: str):
#     directory = DirEntry(
#         path=path,
#         size=0,
#         file_amount=0,
#         files=get_file_entries_from_dir(path)
#     )
#
#     app = DiskMenu(stdscr, path)
#     app.go_to()
