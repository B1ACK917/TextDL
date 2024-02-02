from utils.Crawler.BaseCrawler.Crawler import BaseCrawler


class yrCrawler(BaseCrawler):
    def __init__(self, target):
        super().__init__(r"http://www.yiruan.info/", target)
        self._custom_init()

    def _custom_init(self):
        self._catalog_selector = "#list > dl > dd > a"
        self._bookname_selector = "#info > h1"
        self._author_selector = "#info > p:nth-child(2)"
        self._last_update_selector = "#info > p:nth-child(5)"
        self._intro_selector = "#intro > p:nth-child(1)"
        self._content_selector = "#content"
        self._encode_type = "ISO-8859-1"

    @staticmethod
    def _beautify_content(content):
        for tip in content.select("#content_tip"):
            tip.decompose()
        return content
