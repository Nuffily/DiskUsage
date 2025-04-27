import curses
from datetime import datetime
import os

from scrollable_list import to_papkas


def main(stdscr):
    curses.curs_set(0)  # Скрываем курсор
    options = ["К дискам", "Информация", "Выход"]
    current = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Заголовок
        stdscr.addstr(0, w // 8, "DiskUsage. Меню", curses.A_BOLD)

        # Пункты меню
        for i, opt in enumerate(options):
            x = 0
            y = h // 2 - len(options) // 2 + i
            prefix = "> " if i == current else "  "
            attr = curses.A_REVERSE if i == current else curses.A_NORMAL
            stdscr.addstr(y, x, f"{prefix}{opt}", attr)

        # Подсказка
        stdscr.addstr(h - 1, 0, "↑/↓: выбор • Enter: подтвердить • Q: выход")

        key = stdscr.getch()
        if key == curses.KEY_UP:
            current = max(0, current - 1)
        elif key == curses.KEY_DOWN:
            current = min(len(options) - 1, current + 1)
        elif key == 10:  # Enter
            if current == len(options) - 1:
                break
            if current == len(options) - 3:
                to_papkas(stdscr, 'C:/users/max/desktop')
            if current == len(options) - 2:
                info(stdscr)

        elif key == ord("q"):  # ESC
            break
        elif key == ord("й"):  # ESC
            break

def info(stdscr):
    curses.curs_set(0)  # Скрываем курсор
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        stdscr.addstr(0, w // 8, "DiskUsage. Меню", curses.A_BOLD)

        stdscr.addstr(2, 0, "Это программа, позволяющая посмотреть занимаемое место на диске")
        stdscr.addstr(4, 0, "Показывает, что есть и сколько занимает памяти в любой папке")
        stdscr.addstr(5, 0, "Разумеется, содержимое папок можно сортировать")
        stdscr.addstr(7, 0, "Сделано на матмехе")

        stdscr.addstr(h - 1, 0, "Q: выход")

        key = stdscr.getch()
        if key == ord("q"):  # ESC
            break
        elif key == ord("й"):  # ESC
            break

curses.wrapper(main)