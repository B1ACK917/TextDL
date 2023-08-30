from utils.Crawler.BaseCrawler.Crawler import BaseCrawler


class qulaCrawler(BaseCrawler):
    def __init__(self, target):
        super().__init__(r"https://www.qu-la.com", target)
        self._custom_init()

    def _custom_init(self):
        self._catalog_selector = (
            "#list > div.book-chapter-list > ul:nth-child(4) > li > a"
        )
        self._bookname_selector = "#list > div.book-main > div.book-text > h1"
        self._author_selector = "#list > div.book-main > div.book-text > span"
        self._last_update_selector = "#list > div.block-title > p.update-text > span"
        self._intro_selector = "#list > div.book-main > div.book-text > div.intro"
        self._content_selector = "#txt"

    @staticmethod
    def _beautify_content(content):
        content.a.extract()
        return content
