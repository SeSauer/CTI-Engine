from typing import Protocol

import psutil

from src.fetcher.FetcherInterface import FetcherInterface
from src.fetcher.process_fetcher.CProcess import CProcess
from src.fetcher.process_fetcher.process_observer.ProcessCollector import ProcessCollector
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.ProcessPoint import ProcessPoint


class DataFetcher(FetcherInterface, Protocol):

    __process_collector: ProcessCollector = None
    __data_observer: DataObserver = None
    __model: Model = None

    def add_data_entry(self, process_point: ProcessPoint):
        raise NotImplemented

    def fetch_metrics(self, process: CProcess) -> ProcessPoint:
        raise NotImplemented

    def update_project(self) -> bool:
        raise NotImplemented
