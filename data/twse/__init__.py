from html.parser import HTMLParser


class DataHTMLParser(HTMLParser):

    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)

        self._data = None

    @property
    def error(self) -> bool:
        raise NotImplementedError

    @property
    def data(self) -> dict:
        return self._data
