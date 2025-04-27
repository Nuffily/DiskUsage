import collections
import curses
import os
import string
from curses import wrapper
from datetime import datetime
from importlib.metadata import files
from typing import NamedTuple, List


class MyFile(NamedTuple):
    name: str
    modified: int
    size: int
    is_dir: bool


class ScrollableList:
    def __init__(self, stdscr, files, path):
        self.stdscr = stdscr
        self.files = files
        self.top_idx = 0
        self.selected_idx = 0
        self.path = path
        self.setup_curses()
        self.stack = collections.deque[List[MyFile]]()
        self.title = path
        self.sort_filter = "По расширению"

    def next_dir(self, path):
        self.top_idx = 0
        self.selected_idx = 0
        self.path = path
        self.title = path
        self.stack.append(self.files)
        self.files = [MyFile(
            name=f,
            size=0,
            modified=int(os.path.getmtime(path + "/" + f)),
            is_dir=os.path.isdir(path + "/" + f))
            for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) | os.path.isdir(os.path.join(path, f))
                                         and not os.path.islink(os.path.join(path, f))]

    def back_dir(self):
        self.top_idx = 0
        self.selected_idx = 0

        if len(self.stack):
            self.files = self.stack.pop()
            self.path = os.path.dirname(self.path)
            self.title = self.path
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

        # Заголовок
        title = "-" * 4 + self.title[:self.screen_width - 1] + "-" * (
                self.screen_width - 4 - len(self.title[:self.screen_width - 1]))
        self.stdscr.addstr(0, 0, title, curses.A_BOLD)
        self.stdscr.addstr(self.screen_height - 1, 0,
                           f"↑/↓: прокрутка, Enter: перейти, U: вычислить занимаемое место, S: Сортировка, C: сменить сортировку (сейчас - {self.sort_filter}), Q: назад"[
                           :self.screen_width - 1])
        self.title = self.path
        # Список элементов
        for i in range(self.visible_rows):
            item_idx = self.top_idx + i
            if item_idx >= len(self.files):
                break

            prefix = "> " if item_idx == self.selected_idx else "  "
            item_text = prefix + self.elem_to_str(item_idx)
            attr = curses.A_REVERSE if item_idx == self.selected_idx else curses.A_NORMAL
            self.stdscr.addstr(i + 2, 0, item_text[:self.screen_width - 1], attr)

        self.stdscr.refresh()

    def handle_input(self):
        try:
            key = self.stdscr.getch()

            # Обработка нажатий клавиш
            if key == curses.KEY_UP:
                self.move_selection(-1)
            elif key == curses.KEY_DOWN:
                self.move_selection(1)
            elif key == curses.KEY_PPAGE:  # Page Up
                self.move_selection(-self.visible_rows)
            elif key == curses.KEY_HOME:  # Page Up
                self.move_selection(-9999)
            elif key == curses.KEY_END:  # Page Up
                self.move_selection(9999)
            elif key == curses.KEY_NPAGE:  # Page Down
                self.move_selection(self.visible_rows)
            elif key == ord("u"):  # Page Down
                self.scan()
            elif key == ord("s"):  # Page Down
                self.sort()
            elif key == ord("c"):  # Page Down
                self.change_sort()
            elif key == 10:  # Enter
                self.select_item()
            elif key == ord('q') or key == ord('й'):  # ESC
                # return False
                return self.back_dir()
            return True
        except:
            return True

    def move_selection(self, delta):
        new_idx = max(0, min(self.selected_idx + delta, len(self.files) - 1))
        if new_idx != self.selected_idx:
            self.selected_idx = new_idx
            # Автопрокрутка
            if self.selected_idx < self.top_idx:
                self.top_idx = self.selected_idx
            elif self.selected_idx >= self.top_idx + self.visible_rows:
                self.top_idx = self.selected_idx - self.visible_rows + 1

    def select_item(self):
        if self.files[self.selected_idx].is_dir:
            path = self.path + "/" + self.files[self.selected_idx].name
            self.next_dir(path)
        else:
            self.title = "Передвигаться можно только по папкам"

    def run(self):
        running = True
        while running:
            self.update_window_size()
            self.draw()
            running = self.handle_input()

    def elem_to_str(self, index: int):
        current = self.files[index]

        name = (current.name + (40 - len(current.name)) * " " if len(current.name) < 40 else (
                current.name[:37] + "..."))
        modified = datetime.fromtimestamp(current.modified).strftime(
            '%Y-%m-%d %H:%M:%S')
        size = (str(current.size) if current.size != 0 else "-")
        is_dir = "Да" if current.is_dir else "Нет"

        return name + " | " + modified + " | " + size + " | " + is_dir

    def change_sort(self):
        if self.sort_filter == "По расширению":
            self.sort_filter = "По времени последнего изменения"
        elif self.sort_filter == "По времени последнего изменения":
            self.sort_filter = "По размеру"
        elif self.sort_filter == "По размеру":
            self.sort_filter = "По количеству файлов"
        elif self.sort_filter == "По количеству файлов":
            self.sort_filter = "По расширению"

    def sort(self):
        if self.sort_filter == "По расширению":
            self.files = sorted(self.files, key=lambda x: os.path.splitext(x.name)[1])
        elif self.sort_filter == "По времени последнего изменения":
            self.files = sorted(self.files, key=lambda x: x.modified)
        elif self.sort_filter == "По размеру":
            self.files = sorted(self.files, key=lambda x: -x.size)
        elif self.sort_filter == "По количеству файлов":
            self.files = sorted(self.files, key=lambda x: -get_kolvo(self.path + "/" + x.name))

    def scan(self):
        self.progress = 0
        self.total_size = 0
        self.file_count = 0
        self.skipped_files = 0
        self.stdscr.addstr(1, 0, "Начальный подсчет...")
        self.stdscr.refresh()

        total_files = 0
        for root, dirs, files in os.walk(self.path):
            try:
                total_files += len(files)
            except PermissionError:
                self.skipped_files += len(files)
                continue
        self.obxod(total_files)

    def _calculate_size(self, path, total_files):
        """Вычисляет размер с обновлением прогресс-бара"""
        current_size = self.total_size

        try:
            with os.scandir(path) as it:
                for entry in it:
                    try:

                        if entry.is_symlink():
                            continue

                        if entry.is_file():
                            self.total_size += entry.stat().st_size
                            self.file_count += 1
                            self.progress = self.file_count / (total_files + 1)  # +1 чтобы избежать деления на 0
                        elif entry.is_dir():

                            self._calculate_size(entry.path, total_files)

                    except (PermissionError, FileNotFoundError):
                        self.skipped_files += 1
                    finally:
                        self.draw_bar()
        except PermissionError:
            self.skipped_files += 1

        return self.total_size - current_size

    def obxod(self, total_files):

        for i in range(len(self.files)):

            if os.path.islink(self.path + "/" + self.files[i].name):
                continue

            if not self.files[i].is_dir:
                self.files[i] = MyFile(
                    name=self.files[i].name,
                    is_dir=self.files[i].is_dir,
                    modified=self.files[i].modified,
                    size=os.path.getsize(self.path + "/" + self.files[i].name)
                )

            else:

                self.files[i] = MyFile(
                    name=self.files[i].name,
                    is_dir=self.files[i].is_dir,
                    modified=self.files[i].modified,
                    size=self._calculate_size(self.path + "/" + self.files[i].name, total_files)
                )

    def draw_bar(self):
        bar_width = self.screen_width // 4 - 4
        filled = int(self.progress * bar_width)

        progress_bar = "[" + "#" * filled + " " * (bar_width - filled) + "] " + str(int(self.progress * 100)) + " %"
        self.stdscr.addstr(1, 0, progress_bar)
        self.stdscr.refresh()


def get_kolvo(path):
    total_files = 0
    for root, dirs, files in os.walk(path):
        try:
            total_files += len(files)
        except PermissionError:
            continue
    return total_files


def to_papkas(stdscr, path: str):
    files = [
        MyFile(
            name=f,
            size=0,
            modified=int(os.path.getmtime(path + "/" + f)),
            is_dir=os.path.isdir(path + "/" + f),
        )  # Получаем владельца файла
        for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) | os.path.isdir(os.path.join(path, f))
                                     and not os.path.islink(os.path.join(path, f))]

    app = ScrollableList(stdscr, files, path)
    app.run()

# if __name__ == "__main__":
#     print("Листаемый список - используйте стрелки для навигации")
#     wrapper(to_papkas, 'C:/users/max')
#     print("Работа со списком завершена")
