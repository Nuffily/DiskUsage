from typing import NamedTuple, List


class FileEntry(NamedTuple):
    name: str
    modified: int
    size: int
    is_dir: bool

class DirEntry(NamedTuple):
    path: str
    files: List[FileEntry]
    size: int
    file_amount: int
