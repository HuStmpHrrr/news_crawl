from __future__ import unicode_literals
from crawler.commons import structure
from bs4 import BeautifulSoup
import urlparse
import logging
import demjson


para_class = 'zn-body__paragraph'


def _normal_parser(response):

    def _extract_author():
        authors = ''.join(
            response.css(r'span.metadata__byline__author ::text').extract()).split(', ')
        if len(authors) and authors[0].startswith("By "):
            authors[0] = authors[0][3:]
        if len(authors) and authors[-1] == 'CNN':
            authors.pop()
        if len(authors):
            authors = authors + authors.pop().split(" and ")
        return authors

    title = response.css(r'h1.pg-headline::text').extract_first()
    authors = _extract_author()
    date = response.css('div.metadata__info>.update-time::text').extract_first()

    body = response.css('div.pg-rail-tall__body')
    hl = structure.Highlights(body.css('div.el__storyhighlights ul>li::text').extract())

    structures = []

    cite = body.css('div.el__leafmedia--sourced-paragraph>p.zn-body__paragraph')
    if len(cite):
        source = cite.css('cite::text').extract_first()
        quote = cite.css('::text').extract_first()
        structures.append(structure.Citation(source, quote))

    soup = BeautifulSoup(body.css('.l-container').extract_first(), 'html.parser')
    paragraphs = soup.select('div.l-container > [class^=zn]')

    def _extract_paragraph(para):
        return ''.join(unicode(p) for p in para.contents)

    def _extract_image(para):
        return (para.select_one('img.media__image')['data-src-medium'],
                para.select_one('.media__caption div').string)

    def _extract_sections(para):
        structs = []
        for content in para.contents:
            if para_class in content['class']:
                structs.append(structure.Paragraph(_extract_paragraph(content)))
            elif 'el__embedded' in content['class']:
                try:
                    structs.append(structure.Image(*_extract_image(content)))
                except:
                    logging.warning("failed to parse this elem from {}: {}".format(response.url, content))
                    pass
        return structs

    for para in paragraphs:
        if para_class in para['class']:
            structures.append(structure.Paragraph(_extract_paragraph(para)))
        elif 'zn-body__read-all' in para['class']:
            structures.append(structure.Section(_extract_sections(para)))

    return structure.Article(title, response.url, authors, date, hl, structures)


# TODO: the same idea as above. don't want to spend time on checking out HTML structure
def _money_parser(response):
    pass


def to_structure(response):
    u = urlparse.urlparse(response.url)
    if u.netloc == 'www.cnn.com':
        return _normal_parser(response)
    elif u.netloc == 'money.cnn.com':
        return _money_parser(response)
    else:
        return None


def extract_content_model(response):
    """
    this is very hacky. CNN mainpages are not static so it's a bit tricky
    """
    scripts = [s.css('::text').extract_first() for s in response.css('script')]
    content_scripts = [i for i in scripts if i is not None
                       and i.startswith('var')
                       and 'contentModel' in i]
    try:
        content_script = content_scripts[0]
        jsobj = content_script.split('=', 2)[2].strip()
        jsobj = jsobj[:-1] if jsobj[-1] == ';' else jsobj
        content_model = demjson.decode(jsobj)
        contents = []
        for content in filter(lambda s: 'uri' in s and not s['uri'].startswith('/videos'),
                              content_model['siblings']['articleList']):
            try:
                fields = [content[k] for k in structure.Content._fields[:4]]
                fields.append(response.urljoin(content['uri']))
                contents.append(structure.Content(*fields))
            except Exception as e:
                logging.error(e)
        return contents
    except:
        logging.warning("response from {} cannot be analyzed.".format(response.url))
        return []
