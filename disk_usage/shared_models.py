import curses
from enum import Enum

from pydantic import BaseModel


class FileEntry(BaseModel):
    name: str
    modified: int
    size: int
    is_dir: bool


class DirEntry(BaseModel):
    path: str
    files: list[FileEntry]
    size: int
    file_amount: int


class SortFilter(Enum):
    BY_EXTENSION = "По расширению"
    BY_MODIFIED = "По времени изменения"
    BY_SIZE = "По размеру"
    BY_COUNT = "По количеству файлов"


class CursesKeys(Enum):
    UNKNOWN = 0
    UP = 1
    DOWN = 2
    PAGE_UP = 3
    PAGE_DOWN = 4
    HOME = 5
    END = 6
    UPDATE = 7
    SORT = 8
    CHANGE_SORT = 9
    QUIT = 10
    ENTER = 11

    @staticmethod
    def get(key: int) -> "CursesKeys":
        match key:
            case curses.KEY_UP:
                return CursesKeys.UP
            case curses.KEY_DOWN:
                return CursesKeys.DOWN
            case curses.KEY_PPAGE:
                return CursesKeys.PAGE_UP
            case curses.KEY_NPAGE:
                return CursesKeys.PAGE_DOWN
            case curses.KEY_HOME:
                return CursesKeys.HOME
            case curses.KEY_END:
                return CursesKeys.END
            case 117 | 85 | 1043 | 1075:
                return CursesKeys.UPDATE
            case 115 | 83 | 1067 | 1099:
                return CursesKeys.SORT
            case 99 | 67 | 1089 | 1057:
                return CursesKeys.CHANGE_SORT
            case 113 | 81 | 1081 | 1049:
                return CursesKeys.QUIT
            case 10:
                return CursesKeys.ENTER
            case _:
                return CursesKeys.UNKNOWN
