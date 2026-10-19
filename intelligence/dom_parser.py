from html.parser import HTMLParser

class MioloParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = []
        self.classes = []
        
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        for k, v in attrs:
            if k == 'id': self.ids.append(v)
            if k == 'class': self.classes.extend(v.split())

def ler_miolo(html):
    parser = MioloParser()
    parser.feed(html)
    return {
        "tags": list(set(parser.tags)),
        "ids": list(set(parser.ids)),
        "classes": list(set(parser.classes)),
        "tamanho": len(html)
    }