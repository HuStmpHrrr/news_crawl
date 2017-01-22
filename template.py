from __future__ import unicode_literals
from wheezy.template.engine import Engine
from wheezy.template.loader import DictLoader
from wheezy.template.ext.core import CoreExtension
import sys
import os
from datetime import datetime
from datarepr import structure
import json
import pytz
import calendar
import io

TOP = 25

def render(template, context):
    engine = Engine(
        loader=DictLoader({'x': template}),
        extensions=[CoreExtension()])
    temp = engine.get_template('x')
    return temp.render(context)


def render_to(f, template, context):
    print f, template, context
    with io.open(f, 'w') as fd:
        fd.write(render(template, context))


""" this is sad, CNN doesn't use standard timezone format """
_known_tz = {
    'ET': pytz.timezone("US/Eastern")
}


month_num = dict((v, k) for k, v in enumerate(calendar.month_name) if k != 0)


def parse_time(s):
    """
    not sure how this time on the website is generated,
    so let's make it as fragile as possible
    """
    elems = s.split()
    hour, minute = map(int, elems[1].split(':'))
    if hour == 12:
        hour -= 12
    if elems[2].lower() == 'pm':
        hour += 12
    tz = elems[3][:-1]
    if tz not in _known_tz:
        raise LookupError("unknown timezone: " + tz)
    loc = _known_tz[tz]
    mon = month_num[elems[5]]
    day = int(elems[6][:-1])
    year = int(elems[7])

    return datetime(year, mon, day, hour, minute, 0, tzinfo=loc)


def save_preview(article, folder):
    save_file = article.orig.split('/')[-2] + '.html'

    if os.path.exists(save_file): return save_file

    def _to_paragraph(s):
        """
        since all Paragraphs and Citations are escaped, we can just do
        string interpolation
        """
        return '<div class="paragraph">{}</div>'.format(s.content) if isinstance(s, structure.Paragraph) \
            else '<div class="paragraph">{} - {}</div>'.format(s.source, s.quote)

    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    meta = '<div class="meta">By {}, At {}</div>'.format(', '.join(article.authors),
                                                         parse_time(article.date).strftime(fmt))

    orig_link = '<div class="alert alert-info"><a href="{}">Click here to view original article</a></div>'.format(
        article.orig)

    body = ''.join(_to_paragraph(s) for s in article.structures
                   if isinstance(s, structure.Paragraph) or isinstance(s, structure.Citation))

    with io.open(os.path.join(folder, save_file), 'w') as fd:
        fd.write(meta + orig_link + body)

    return save_file

if __name__ == '__main__':
    work_folder = sys.argv[1]
    source = sys.argv[2]
    templatef = os.path.join(work_folder, 'index.html.tpl')
    outputf = os.path.join(work_folder, 'index.html')
    prevf = os.path.join(work_folder, 'previews')
    targetf = os.path.join(work_folder, 'targets')

    try:
        os.makedirs(prevf)
    except OSError as e:
        if e.errno != 17: raise e

    with open(templatef) as fd:
        template = fd.read()

    targets = {}

    for target in [f for f in os.listdir(targetf)
                     if os.path.splitext(f)[1] == '.jsonl']:
        t = os.path.splitext(target)[0]
        with open(os.path.join(targetf, target)) as fd:
            articles = [structure.fromdict(json.loads(l)) for l in fd]

        items = []
        for article in articles:
            preview = 'previews/' + save_preview(article, prevf)
            time = parse_time(article.date)
            items.append(structure.NewsItem(article.title, time, article.highlights, preview))
        targets[t] = items

    context = { 'targets': targets, 'source': source }
    render_to(outputf, template, context)
