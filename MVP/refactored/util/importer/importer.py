from abc import ABC, abstractmethod
from typing import TextIO
from typing import List

from MVP.refactored.frontend.components.custom_canvas import CustomCanvas


class Importer(ABC):

    def __init__(self, canvas):
        self.canvas: CustomCanvas = canvas

    @abstractmethod
    def start_import(self, files: List[TextIO]) -> str:
        pass

    @abstractmethod
    def load_everything_to_canvas(self, data: dict, canvas: CustomCanvas):
        pass
