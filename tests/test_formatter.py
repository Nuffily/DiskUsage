import pytest

from disk_usage.formatter import Formatter
from disk_usage.shared_models import FileEntry, SortFilter


class TestFormatter:
    @pytest.fixture
    def formatter(self) -> Formatter:
        return Formatter()

    @pytest.mark.parametrize(
        "title, width, expected", [("test", 10, "----test--"), ("long_title_that_exceeds_width", 7, "----long_t")]
    )
    def test_formatter_get_title(self, title: str, width: int, expected: str, formatter: Formatter) -> None:
        assert formatter.get_title(title, width) == expected

    @pytest.mark.parametrize(
        "input_value, expected",
        [(1672142512, "2022-12-27 17:01:52"), (363431213, "1981-07-08 14:06:53"), (963431213, "2000-07-13 00:46:53")],
    )
    def test_formatter_get_time(self, input_value: int, expected: str, formatter: Formatter) -> None:
        file_entry = FileEntry(name="test", modified=input_value, size=0, is_dir=False)
        assert formatter.get_time(file_entry) == expected

    @pytest.mark.parametrize(
        "input_value, expected",
        [(1024, "1.00 Kb   "), (2200, "2.15 Kb   "), (1073741824, "1.00 Gb   "), (0, "-"), (6, "6 b       ")],
    )
    def test_formatter_get_size(self, input_value: int, expected: str, formatter: Formatter) -> None:
        file_entry = FileEntry(name="test", modified=0, size=input_value, is_dir=False)
        assert formatter.get_size(file_entry) == expected

    @pytest.mark.parametrize(
        "input_value, expected",
        [
            (SortFilter.BY_EXTENSION, "По расширению"),
            (SortFilter.BY_SIZE, "По размеру"),
            (SortFilter.BY_MODIFIED, "По времени изменения"),
            (SortFilter.BY_COUNT, "По количеству файлов"),
        ],
    )
    def test_formatter_get_sort_filter(self, input_value: SortFilter, expected: str, formatter: Formatter) -> None:
        assert formatter.get_sort_filter(input_value) == expected
