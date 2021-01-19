import io
from typing import Generator, List


class Line:
    target_line_no: int
    is_added: bool


class Hunk:
    def target_lines(self) -> List[Line]:
        ...


class PatchedFile:
    is_binary_file: bool
    is_removed_file: bool
    path: str

    def __iter__(self) -> Generator[Hunk, None, None]:
        ...


class PatchSet:
    def __init__(self, input: io.IOBase):
        ...

    def __iter__(self) -> Generator[PatchedFile, None, None]:
        ...
