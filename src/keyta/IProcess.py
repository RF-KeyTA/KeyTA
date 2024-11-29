from abc import abstractmethod


class IProcess:
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass
