import curses

import _curses

from disk_usage.shared_models import CursesKeys


class InfoMenu:
    """Информационное меню"""

    def __init__(self, stdscr: _curses.window):
        self.stdscr = stdscr

    def go_to(self) -> None:
        """Переход в окно информации"""
        while True:
            self.stdscr.clear()
            height, width = self.stdscr.getmaxyx()

            self.stdscr.addstr(0, width // 8, "DiskUsage. Меню", curses.A_BOLD)

            self.stdscr.addstr(2, 0, "Это программа, позволяющая посмотреть занимаемое место на диске")
            self.stdscr.addstr(4, 0, "Показывает, что есть и сколько занимает памяти в любой папке")
            self.stdscr.addstr(5, 0, "Разумеется, содержимое папок можно сортировать")
            self.stdscr.addstr(7, 0, "Сделано на матмехе")

            self.stdscr.addstr(height - 1, 0, "Q: выход")

            key = CursesKeys.get(self.stdscr.getch())

            if key == CursesKeys.QUIT:
                break
