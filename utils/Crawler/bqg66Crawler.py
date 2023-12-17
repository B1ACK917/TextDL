from utils.Crawler.BaseCrawler.Crawler import BaseCrawler


class bqg66Crawler(BaseCrawler):
    def __init__(self, target):
        super().__init__(r"https://www.biquge66.net", target)
        self._custom_init()

    def _custom_init(self):
        self._catalog_selector = "#haitung"
        self._bookname_selector = "#info > h1"
        self._author_selector = "#info > p:nth-child(2) > a"
        self._last_update_selector = "#info > div > p:nth-child(3)"
        self._intro_selector = "#intro"
        self._content_selector = "#booktxt"

    @staticmethod
    def _beautify_content(content):
        return content
