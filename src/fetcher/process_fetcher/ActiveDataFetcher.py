import os
from typing import List
import psutil
from builder.BuilderInterface import BuilderInterface
from builder.header_builder.CompilingTool import CompilingTool
from fetcher.FetcherInterface import FetcherInterface
from fetcher.process_fetcher.process_observer.ProcessCollector import ProcessCollector
from fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import (
    DataObserver,
)
from model.Model import Model
from model.core.DataEntry import DataEntry
from model.core.ProcessPoint import ProcessPoint
from model.core.SourceFile import SourceFile


class ActiveDataFetcher(FetcherInterface):
    def update_project(self) -> bool:
        self.__header_name: str = self.__compiling_tool.get_next_header_name()
        more_to_build: bool = self.__compiling_tool.build()
        found_header: bool = True
        self.__header_proc: psutil.Process = None
        found_header = self.search_for_header()
        while found_header:
            found_header = self.search_for_header()
            if found_header:
                process_point: ProcessPoint = self.__fetch_metrics(
                    self.__header_proc)
                self.__add_data_entry(process_point)

    def search_for_header(self) -> bool:
        processes: List[psutil.Process] = self.__process_collector.catch_processes(
        )
        for process in processes:
            if ActiveDataFetcher.filter_for_str(
                    process, self.__header_name):
                self.__header_proc = process
                return True
        return False

    def filter_for_str(process: psutil.Process, string: str):
        cmdline: List[str] = process.cmdline()
        for entry in cmdline:
            if string in entry and entry.endswith(".o"):
                return True
        return False

    def __init__(
        self, source_file_name: str, model: Model, build_dir_path: str
    ) -> None:
        self.__model = model
        self.__source_file: SourceFile = model.get_sourcefile_by_name(
            source_file_name)
        self.__data_observer = DataObserver()
        self.__process_collector = ProcessCollector(-1)
        self.__compiling_tool: BuilderInterface = CompilingTool(
            self.__source_file, build_dir_path
        )  # TODO

    def __fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.data_observer.observe(process)

    def __add_data_entry(self, process_point: ProcessPoint):
        path: str = self.__model.current_project.working_dir
        cmdline: List[str] = process_point.process.cmdline()
        path = self.__header_name
        self.__model.insert_datapoints(
            [DataEntry(path, process_point.metrics, process_point.timestamp)]
        )
