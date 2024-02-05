from src.model.core.SourceFile import SourceFile
from src.model.core.Header import Header
from typing import cast


class HeaderIterator:
    """iterator class for headers in a source file to a given depth"""

    def __init__(self, source_file: SourceFile, depth: int):
        self.source_file: SourceFile = source_file
        self.headers: list[Header] = self.__get_all_headers(depth)
        self.index: int = 0

    def __get_all_headers(self, depth: int) -> list[Header]:
        all_headers: list[Header] = list()
        header_ranks: list[list[Header]] = []
        header_ranks[0] = cast(list[Header], self.source_file.header)

        for x in range(1, depth + 1):
            for header in header_ranks[x-1]:
                header_ranks[x].extend(cast(list[Header], header.header))

        for rank in header_ranks:
            all_headers.extend(rank)

        return all_headers

    def get_next_header(self) -> Header:
        """returns the next header from the source file"""
        return self.headers[self.index]
    
    def pop_next_header(self) -> Header:
        """returns the next header from the source file"""
        self.index += 1
        return self.headers[self.index - 1]

    def has_next_header(self) -> bool:
        """returns true if one or more headers can still be retrieved from the iterator"""
        return self.index < len(self.headers) - 1
