from scrapy.dupefilter import RFPDupeFilter
import urlparse
from w3lib.url import canonicalize_url


class UrlOnlyFilter(RFPDupeFilter):
    def request_fingerprint(self, request):
        url = urlparse.urlparse(request.url)
        curl = canonicalize_url(url._replace(query='', params='', fragment='').geturl())
        return curl
