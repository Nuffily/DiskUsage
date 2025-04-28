import curses
import os
import string
from typing import List

from disk_usage.disk_menu import DiskMenu


class DiskPickMenu:
    """Меню выбора диска"""

    def __init__(self, stdscr) -> None:
        self._stdscr = stdscr
        self._disks = [d for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
        self._current = 0

    def go_to(self) -> None:
        """
        Переходит в меню для выбора диска, который будет подан в DiskMenu, только для Windows
        В случае с Posix - сразу переходит к DiskMenu
        """

        if os.name == "posix":
            DiskMenu(self._stdscr, '/').go_to()

        while True:
            self._stdscr.clear()
            height, width = self._stdscr.getmaxyx()

            self._stdscr.addstr(0, width // 8, "DiskUsage. Выберите диск", curses.A_BOLD)
            self._stdscr.addstr(height - 1, 0, "Enter: подтвердить • Q: назад")

            self._create_list(height)

            if not self._handle_input():
                break

    def _handle_input(self) -> bool:
        """
        Принимает нажатие клавиши, позволяет листать список
        Возвращает False, если была нажата клавиша приводящая в окончанию программы
        """
        key = self._stdscr.getch()

        if key == curses.KEY_UP:
            self._current = max(0, self._current - 1)
        elif key == curses.KEY_DOWN:
            self._current = min(len(self._disks) - 1, self._current + 1)
        elif key == 10:  # Enter
            DiskMenu(self._stdscr, self._disks[self._current] + ':/').go_to()
        elif key in (ord("q"), ord("й"), ord("Q"), ord("Й")):  # Выход
            return False

        return True

    def _create_list(self, height: int):
        """Создает список листаемых опций из disks"""
        for i, opt in enumerate(self._disks):
            x = 0
            y = height // 2 - len(self._disks) // 2 + i
            prefix = "> " if i == self._current else "  "
            attr = curses.A_REVERSE if i == self._current else curses.A_NORMAL
            self._stdscr.addstr(y, x, f"{prefix}{opt}", attr)