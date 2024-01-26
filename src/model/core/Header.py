from typing import List

from src.model.core.CFile import CFile


class Header(CFile):

    def __init__(self, path: str):
        super(Header, self).__init__(path)

    def get_timestamps(self) -> List[float]:
        timestamps: List[float] = list()
        for datapoint in self.data_entries:
            timestamps.append(datapoint.timestamp)
        return timestamps
