from typing import List
from model.core.CFile import CFile
from model.core.FileDictionary import FileDictionary
from src.model.core.SourceFile import SourceFile


class Project:
    """Project models a CMake-Project and represents a tracked project with its tracked CFiles."""
    source_files: List[SourceFile] = list()

    def __init__(self, working_dir: str, origin_pid: int, path_to_save: str):
        self.working_dir = working_dir
        self.origin_pid = origin_pid
        self.path_to_save = path_to_save
        self.file_dict = FileDictionary()

    def get_sourcefile(self, name: str) -> SourceFile:
        return self.file_dict.get_file_by_name(name)
