from Crawler.BaseCrawler.Crawler import BaseCrawler


class qulaSpider(BaseCrawler):
    def __init__(self, target):
        super().__init__(r"https://www.qu-la.com", target)

    def _custom_init(self):
        self._catalog_selector = None
        self._bookname_selector = None
        self._author_selector = None
        self._last_update_selector = None
        self._intro_selector = None
        self._content_selector = None

    @staticmethod
    def _beautify_content(content):
        content.a.extract()
        return content
