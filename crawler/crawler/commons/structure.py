from collections import namedtuple


class Structure(object):
    pass


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


Content = namedtuple("Content", 'description, duration, headline, thumbnail, uri')
