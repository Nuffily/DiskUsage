import curses

import _curses

from disk_usage.disk_pick_menu import DiskPickMenu
from disk_usage.info_menu import InfoMenu
from disk_usage.shared_models import CursesKeys


class MainMenu:
    """Основное окно программы"""

    def __init__(self, stdscr: _curses.window):
        """Основной цикл программы"""
        self._options = ["К дискам", "Информация", "Выход"]
        self._current = 0
        self._stdscr = stdscr
        self._info_menu = InfoMenu(stdscr)
        self._disk_menu = DiskPickMenu(stdscr)

        curses.curs_set(0)
        curses.use_default_colors()

        while True:
            self._stdscr.clear()
            height, width = self._stdscr.getmaxyx()

            self._stdscr.addstr(0, width // 8, "DiskUsage. Меню", curses.A_BOLD)
            self._stdscr.addstr(height - 1, 0, "Enter: подтвердить • Q: выход")

            self._create_list(height)

            if not self._handle_input():
                break

    def _handle_input(self) -> bool:
        """
        Принимает нажатие клавиши, позволяет листать список
        Возвращает False, если была нажата клавиша приводящая в окончанию программы
        """
        key = self._stdscr.getch()

        match CursesKeys.get(key):
            case CursesKeys.UP:
                self._current = max(0, self._current - 1)
            case CursesKeys.DOWN:
                self._current = min(len(self._options) - 1, self._current + 1)
            case CursesKeys.ENTER:
                if self._current == 0:  # К дискам
                    self._disk_menu.go_to()
                if self._current == 1:  # Информация
                    self._info_menu.go_to()
                if self._current == 2:  # Выход
                    return False
            case CursesKeys.QUIT:
                return False

        return True

    def _create_list(self, height: int) -> None:
        """Создает список листаемых опций из options"""
        for i, opt in enumerate(self._options):
            x = 0
            y = height // 2 - len(self._options) // 2 + i
            prefix = "> " if i == self._current else "  "
            attr = curses.A_REVERSE if i == self._current else curses.A_NORMAL
            self._stdscr.addstr(y, x, f"{prefix}{opt}", attr)


if __name__ == "__main__":
    curses.wrapper(MainMenu)
