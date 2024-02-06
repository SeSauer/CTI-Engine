from typing import Protocol
from src.model.ModelReadViewInterface import ModelReadViewInterface

class UIInterface(Protocol):
    """provides an Interface for Implemetations of a User Interface. All contained Methods must be implemented by subclasses."""

    def visualize(self, model: ModelReadViewInterface):
        """receives a Model, displays the data contained in that Model to the user."""
        raise NotImplementedError

    def deploy_error(self, error: BaseException):
        """receives an Exception, displays information regarding that exception to the user."""
        raise NotImplementedError
    
    def update_statusbar(self, status: str):
        """receives a status string, changes the ui's status string accordingly."""
        raise NotImplementedError
