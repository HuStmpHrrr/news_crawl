from collections import namedtuple


class Structure(object):
    def todict(self):

        def convert(e):
            return e.todict() if isinstance(e, Structure) else \
                   map(convert, e) if isinstance(e, list) else \
                   e

        d = {
            k: convert(v)
            for (k, v) in self._asdict().items()
        }
        d['type'] = self.__class__.__name__
        return d


class Citation(Structure, namedtuple('Citation', 'source, quote')):
    pass


class Paragraph(Structure, namedtuple("Paragraph", "content")):
    pass


class Image(Structure, namedtuple("Image", "path, caption")):

    def __init__(self, path, caption=""):
        super(Image, self).__init__(path, caption)


class ImageSet(Structure, namedtuple("ImageSet", 'images')):
    pass


class Freeform(Structure, namedtuple('Freeform', 'elem')):
    pass


class Section(Structure, namedtuple('Section', 'structures')):
    pass


class Highlights(Structure, namedtuple('Highlights', 'items')):
    pass


class Article(Structure, namedtuple('Article', 'title, orig, authors, date, highlights, structures')):
    pass

_structure_classes = { t.__name__: t
                      for t in globals().values()
                        if isinstance(t, type)
                        and issubclass(t, Structure)
                        and t is not Structure
                      }

def fromdict(d):
    def convert(e):
        return map(convert, e) if isinstance(e, list) else \
               fromdict(e) if isinstance(e, dict) and 'type' in e else \
               e
    clz = _structure_classes[d['type']]
    return clz(**{ f: convert(d[f]) for f in clz._fields })


Content = namedtuple("Content", 'description, duration, headline, thumbnail, uri')


NewsItem = namedtuple("NewsItem", 'title, date, highlights, location')
