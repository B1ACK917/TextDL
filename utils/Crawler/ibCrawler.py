from utils.Crawler.BaseCrawler.Crawler import BaseCrawler


class ibCrawler(BaseCrawler):
    def __init__(self, target):
        super().__init__(r"http://www.ibiquge.cc", target)
        self._custom_init()

    def _custom_init(self):
        self._catalog_selector = "body > div.listmain > dl > dd > a"
        self._bookname_selector = "#info > h1"
        self._author_selector = "#info > p:nth-child(4)"
        self._last_update_selector = "#info > p:nth-child(7)"
        self._intro_selector = "#intro > p:nth-child(1)"
        self._content_selector = "#content"

    @staticmethod
    def _beautify_content(content):
        return content
