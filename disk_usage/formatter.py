from datetime import datetime

from disk_usage.shared_models import FileEntry, DirEntry, SortFilter


class Formatter:
    """Класс для форматирования строк для DiskMenu"""

    def __init__(self):
        self._MEGABYTE = 1048576
        self._GIGABYTE = 1073741824
        self._KILOBYTE = 1024

    def get_title(self, title: str, width: int):
        """Возвращает строку с текущим путем и забитую знаками '-' """
        return "-" * 4 + title[:width - 1] + "-" * (width - 4 - len(title[:width - 1]))

    def get_time(self, file: FileEntry) -> str:
        """Возвращает строку формата %Y-%m-%d %H:%M:%S из поля file.modified"""
        return datetime.fromtimestamp(file.modified).strftime('%Y-%m-%d %H:%M:%S')

    def get_legend(self):
        """Возвращает строку для наименования столбцов таблицы DiskMenu"""
        return "  Имя файла" + " " * 34 + "Дата изменения" + " " * 8 + "Папка" + " " * 3 + "Размер"

    def get_file_name(self, name: str) -> str:
        """Возвращает строку имени файла для таблицы DiskMenu"""
        return name + (40 - len(name)) * " " if len(name) < 40 else (name[:37] + "...")

    def get_list_hint(self, sort_filter: SortFilter):
        """Возвращает строку с подсказками управления DiskMenu"""
        return (f"Enter: перейти • U: вычислить занимаемое место • S: Сортировка • "
                f"C: сменить сортировку (сейчас - {self.get_sort_filter(sort_filter)}) • Q: назад")

    def get_size(self, file: FileEntry) -> str:
        """Возвращает отформатированную строку размера файла для таблицы DiskMenu"""
        size = file.size

        if not size:
            return "-"

        elif size >= self._GIGABYTE:
            size = f"{(size / self._GIGABYTE):.2f} Gb"

        elif size >= self._MEGABYTE:
            size = f"{(size / self._MEGABYTE):.2f} Mb"

        elif size >= self._KILOBYTE:
            size = f"{(size / self._KILOBYTE):.2f} Kb"

        else:
            size = f"{size} b"

        return size + " " * (10 - len(size))

    def get_bar(self, directory_size: int, current_size: int) -> str:
        """Возвращает отформатированную полосу занимаемого места в папке файлом для таблицы DiskMenu"""
        if directory_size and current_size:
            prop = int(current_size / directory_size * 10)
            return "[" + "#" * prop + " " * (10 - prop) + "]"
        else:
            return ""

    def entry_to_str(self, directory: DirEntry, index: int) -> str:
        """Возвращает отформатированную строку файла для таблицы DiskMenu"""
        current = directory.files[index]

        name = self.get_file_name(current.name)
        modified = self.get_time(current)
        size = self.get_size(current)
        is_dir = "Да " if current.is_dir else "Нет"
        bar = self.get_bar(directory.size, current.size)

        return name + " | " + modified + " | " + is_dir + "   | " + size + bar

    def get_sort_filter(self, sort_filter: SortFilter) -> str:
        """Возвращает строку соответствующую значению Енама"""
        if sort_filter == SortFilter.BY_EXTENSION:
            return "По расширению"
        elif sort_filter == SortFilter.BY_SIZE:
            return "По размеру"
        elif sort_filter == SortFilter.BY_MODIFIED:
            return "По времени изменения"
        elif sort_filter == SortFilter.BY_COUNT:
            return "По количеству файлов"
