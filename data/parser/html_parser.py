from html.parser import HTMLParser

from . import DataParser


class DataHTMLParser(DataParser, HTMLParser):
    
    def __init__(self, **kw):
        DataParser.__init__(self, **kw)
        HTMLParser.__init__(self)

        self._stack = []

    def is_in_tag(self, tag):
        return self._stack and self._stack[-1] == tag
    
    def is_in_tags(self, tags):
        return self._stack and self._stack[-len(tags):] == tags
    
    def handle_starttag(self, tag, attrs):
        self._stack.append(tag)
    
    def handle_endtag(self, tag):
        while self._stack and (popped_tag := self._stack.pop()):
            if popped_tag == tag:
                break
