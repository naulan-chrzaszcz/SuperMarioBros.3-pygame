from abc import ABC, abstractmethod


class MapsFactory(ABC):

    @abstractmethod
    def create_map(self):
        pass
