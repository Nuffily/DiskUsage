from enum import Enum
from typing import List

from pydantic import BaseModel


class FileEntry(BaseModel):
    name: str
    modified: int
    size: int
    is_dir: bool


class DirEntry(BaseModel):
    path: str
    files: List[FileEntry]
    size: int
    file_amount: int


class SortFilter(Enum):
    BY_EXTENSION = 0
    BY_MODIFIED = 1
    BY_SIZE = 2
    BY_COUNT = 3
