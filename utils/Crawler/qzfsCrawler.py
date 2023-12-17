from utils.Crawler.BaseCrawler.Crawler import BaseCrawler


class qzfsCrawler(BaseCrawler):
    def __init__(self, target):
        super().__init__(r"http://www.quanzhifashi.com", target)
        self._custom_init()

    def _custom_init(self):
        self._catalog_selector = "body > div.main.clearfix > div.ml_content.clearfix > div.zb > div.ml_list > ul > li > a"
        self._bookname_selector = "body > div.main.clearfix > div.info-box.clearfix > div.catalog > div > div.introduce > h1"
        self._author_selector = "body > div.main.clearfix > div.info-box.clearfix > div.catalog > div > div.introduce > p.bq > span:nth-child(2) > a"
        self._last_update_selector = "body > div.main.clearfix > div.info-box.clearfix > div.catalog > div > div.introduce > p.bq > span:nth-child(1)"
        self._intro_selector = "body > div.main.clearfix > div.info-box.clearfix > div.catalog > div > div.introduce > p.jj"
        self._content_selector = "#articlecontent"

    @staticmethod
    def _beautify_content(content):
        return content
