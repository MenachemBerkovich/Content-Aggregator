# TODO docstring for module and for functions and classes


from abc import ABC, abstractmethod

class Feed(ABC):
    def __init__(self, id: int, url: str) -> None:
        self.id = id
        if not self._is_valid():
            raise ValueError(f"Invalid url: {url}")
    @abstractmethod
    def _is_valid(self) -> bool:
        pass

class RSSFeed(Feed):
    def _is_valid(self) -> bool:
        return

class HTMLFeed(Feed):
    def _is_valid(self) -> bool:
        return


class FeedFactory:
    @staticmethod
    def create(url: str) -> Feed:
        pass
