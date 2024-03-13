from multiprocessing import Queue, Event, Lock
from multiprocessing.synchronize import Event as SyncEvent
from multiprocessing.synchronize import Lock as SyncLock
import os
from os.path import join

from PyQt5.QtCore import pyqtSignal
from src.app.Configuration import Configuration
from src.app.Threads.ActiveFetcherThread import ActiveFetcherThread

from src.app.Threads.FileFetcherThread import FileFetcherThread
from src.app.Threads.FileSaverThread import FileSaverThread
from src.app.Threads.HierarchyThread import HierarchyThread
from src.app.Threads.PassiveDataThread import PassiveDataThread
from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher
from src.app.Threads.GUICommunicationManager import GUICommunicationManager
from src.model.Model import Model
from src.saving.SaveInterface import SaveInterface
from src.saving.SaveToJSON import SaveToJSON

from src.view.AppRequestsInterface import AppRequestsInterface


class App(AppRequestsInterface):
    def __init__(self, shutdown_event: SyncEvent, passive_mode_event: SyncEvent, load_event: SyncEvent,
                 load_path_queue: Queue, source_file_name_queue: Queue, visualize_signal: pyqtSignal,
                 error_queue: Queue, error_signal: pyqtSignal, status_signal: pyqtSignal,
                 status_queue: Queue, project_queue: Queue, cancel_event: SyncEvent, restart_event: SyncEvent, model: Model):
        # Events:
        self.__finished_project_event: SyncEvent = Event()
        self.fetching_passive_data: SyncEvent = Event()
        self.__active_measurement_active: SyncEvent = Event()
        self.__fetching_hierarchy: SyncEvent = Event()

        self.passive_mode_event: SyncEvent = passive_mode_event
        self.shutdown_event: SyncEvent = shutdown_event
        self.load_event: SyncEvent = load_event
        self.__restart_event: SyncEvent = restart_event
        self.__cancel_event: SyncEvent = cancel_event
        self.__hierarchy_fetching_event: SyncEvent = Event()
        self.__hierarchy_fetching_event.set()

        # Queues:
        self.load_path_queue: Queue = load_path_queue
        self.__source_file_name_queue: Queue = source_file_name_queue
        self.__error_queue: Queue = error_queue
        self.status_queue: Queue = status_queue
        self.__project_queue: Queue = project_queue
        self.__hierarchy_fetcher_work_queue: Queue = Queue()
        self.__file_saver_work_queue: Queue = Queue()

        # Model
        self.__model_lock: SyncLock = Lock()
        self.__model = model

        # Signals for GUI
        self.__error_signal: pyqtSignal = error_signal
        self.__status_signal: pyqtSignal = status_signal
        self.visualize_signal: pyqtSignal = visualize_signal

        # Configuration
        self.config: Configuration = Configuration.load(
            "/common/homes/all/udixi_schneider/Documents/git/cti-engine-prototype/config/ConfigFile.json")

        # Saving
        self.saver: SaveInterface = SaveToJSON(self.config.saves_path)

        # Passive Fetching:
        self.__passive_data_fetcher: PassiveDataFetcher = PassiveDataFetcher(self.__model, self.__model_lock,
                                                                             self.__file_saver_work_queue,
                                                                             self.__hierarchy_fetcher_work_queue,
                                                                             self.shutdown_event, self.config.saves_path,
                                                                             self.__project_queue,
                                                                             self.visualize_signal,
                                                                             self.__finished_project_event,
                                                                             self.passive_mode_event,
                                                                             process_finder_count=5,
                                                                             process_collector_count=3,
                                                                             fetcher_count=3,
                                                                             fetcher_process_count=20)

        self.passive_thread: PassiveDataThread = PassiveDataThread(shutdown_event, self.__passive_data_fetcher,
                                                                   self.passive_mode_event, self.fetching_passive_data)

        self.hierarchy_fetcher = HierarchyFetcher(self.__model, self.__model_lock, self.__hierarchy_fetching_event,
                                                  self.shutdown_event)

    def prepare_threads(self):
        self.hierarchy_thread: HierarchyThread = HierarchyThread(self.shutdown_event, self.hierarchy_fetcher,
                                                                 self.__error_queue, self.__hierarchy_fetcher_work_queue,
                                                                 self.__hierarchy_fetching_event,
                                                                 self.__fetching_hierarchy)

        self.file_saver_thread: FileSaverThread = FileSaverThread(self.shutdown_event, self.__model, self.saver,
                                                                  self.__model_lock, self.__finished_project_event,
                                                                  self.__file_saver_work_queue)
        self.file_fetch_thread: FileFetcherThread = FileFetcherThread(self.__error_queue, self.__model,
                                                                      self.__model_lock, self.shutdown_event,
                                                                      self.load_path_queue, self.load_event,
                                                                      self.__project_queue, self.visualize_signal)
        self.__status_and_error_thread: GUICommunicationManager = (
            GUICommunicationManager(shutdown_event=self.shutdown_event, error_queue=self.__error_queue,
                                    error_signal=self.__error_signal, passive_mode_event=self.passive_mode_event,
                                    status_queue=self.status_queue, status_signal=self.__status_signal,
                                    fetching_passive_data=self.fetching_passive_data,
                                    active_measurement_active=self.__active_measurement_active,
                                    finished_project_event=self.__finished_project_event, load_event=self.load_event,
                                    cancel_event=self.__cancel_event, restart_event=self.__restart_event,
                                    hierarchy_fetching_event=self.__hierarchy_fetching_event,
                                    fetching_hierarchy=self.__fetching_hierarchy))
        self.__active_mode_fetcher_thread: ActiveFetcherThread = ActiveFetcherThread(self.shutdown_event,
                                                                                     self.__file_saver_work_queue,
                                                                                     self.config.saves_path,
                                                                                     self.__model,
                                                                                     self.__model_lock,
                                                                                     self.__source_file_name_queue,
                                                                                     self.__error_queue,
                                                                                     self.config.active_build_dir_path,
                                                                                     self.__active_measurement_active,
                                                                                     self.visualize_signal,
                                                                                     self.__project_queue)

    def start(self):
        print("[app]    started")
        self.prepare_threads()

        self.__status_and_error_thread.start()
        self.passive_thread.start()
        self.file_saver_thread.start()
        self.hierarchy_thread.start()
        self.file_fetch_thread.start()

        self.__active_mode_fetcher_thread.start()

    def stop(self):
        self.shutdown_event.set()
        self.passive_thread.stop()
        self.hierarchy_thread.stop()
        self.file_saver_thread.stop()
        self.__status_and_error_thread.stop()
        self.__active_mode_fetcher_thread.stop()
        self.file_fetch_thread.stop()
        print("[App]    stopped")

    def __get_cti_folder_path(self) -> str:
        path: str = ""
        path += join(os.getcwd().split("cti-engine-prototype")[0])
        return path
