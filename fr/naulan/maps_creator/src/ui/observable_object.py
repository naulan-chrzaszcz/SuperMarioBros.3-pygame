from abc import ABC, abstractmethod

from fr.naulan.maps_creator.src.ui.observer import Observer


class ObservableObject(ABC):

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass

