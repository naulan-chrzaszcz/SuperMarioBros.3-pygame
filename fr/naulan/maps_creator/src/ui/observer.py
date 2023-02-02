from abc import ABC, abstractmethod


class Observer(ABC):

    @abstractmethod
    def update(self, observable_object):
        pass

