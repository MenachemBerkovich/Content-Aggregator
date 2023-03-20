class Feed:
    def __init__(self, id: str) -> None:
        self.id = id

class RSSFeed(Feed):
    def __init__(self, url: str) -> None:
        super().__init__(id)

class HTMLFeed(Feed):
    def __init__(self, url: str) -> None:
        super().__init__(id)
        