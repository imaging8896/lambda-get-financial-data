from html.parser import HTMLParser

from . import DataParser


class DataHTMLParser(DataParser, HTMLParser):
    
    def __init__(self, **kw):
        DataParser.__init__(self, **kw)
        HTMLParser.__init__(self)
