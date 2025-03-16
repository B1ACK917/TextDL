from utils.Crawler.BaseCrawler.Crawler import BaseCrawler


class bigeeCrawler(BaseCrawler):
    def __init__(self, target):
        super().__init__(r"https://www.bigee.cc", target)
        self._custom_init()

    def _custom_init(self):
        self._catalog_selector = "body > div.listmain > dl > dd > a"
        self._bookname_selector = "body > div.book > div.info > h1"
        self._author_selector = "body > div.book > div.info > div.small > span:nth-child(1)"
        self._last_update_selector = "body > div.book > div.info > div.small > span:nth-child(3)"
        self._intro_selector = "body > div.book > div.info > div.intro > dl > dd"
        self._content_selector = "#chaptercontent"
        # self._encode_type = "ISO-8859-1"

    def _crawl_catalog(self):
        catalogs = self._homepage.select(self._catalog_selector)
        hidden_catalogs = self._homepage.select("body > div.listmain > dl > span > dd > a")
        for item in catalogs[:10]:
            self._book_catalog.append(
                item.get_text().encode(self._encode_type).decode(self._decode_type, errors="ignore"))
            self._catalog_urls.append(self._server + item.get("href"))
        for item in hidden_catalogs:
            self._book_catalog.append(
                item.get_text().encode(self._encode_type).decode(self._decode_type, errors="ignore"))
            self._catalog_urls.append(self._server + item.get("href"))
        for item in catalogs[10:]:
            self._book_catalog.append(
                item.get_text().encode(self._encode_type).decode(self._decode_type, errors="ignore"))
            self._catalog_urls.append(self._server + item.get("href"))
        self._catalog_num = len(self._book_catalog)

    @staticmethod
    def _beautify_content(content):
        for tip in content.select("#chaptercontent > p"):
            tip.decompose()
        return content
