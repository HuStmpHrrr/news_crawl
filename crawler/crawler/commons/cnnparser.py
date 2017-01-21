from crawler.commons import structure
from bs4 import BeautifulSoup
import urlparse
import logging


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
            authors = authors + authors[-1].split(" and ")
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
        return (para.select_one('img.media__image')['src'],
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
                    logging.warning("failed to parse this elem: {}".format(content))
                    pass
        return structs

    for para in paragraphs:
        if para_class in para['class']:
            structures.append(structure.Paragraph(_extract_paragraph(para)))
        elif 'zn-body__read-all' in para['class']:
            structures.append(structure.Section(_extract_sections(para)))

    return structure.Article(title, response.url, authors, date, hl, structures)


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
