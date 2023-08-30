from Spider.Spider import BaseSpider


class XBiqugeSpider(BaseSpider):
    def __init__(self, target):
        super().__init__(r"http://www.ibiquge.cc", target)
        self._init_others()
        self._text_tag = "#content"

    def _init_information(self):
        pre_name = self.bs.select("#info > h1")
        self._book_name = pre_name[0].get_text()
        pre_author = self.bs.select("#info > p:nth-child(4)")
        self._author = pre_author[0].get_text()
        pre_time = self.bs.select("#info > p:nth-child(7)")
        self._current_time = pre_time[0].get_text()
        pre_intro = self.bs.select("#intro > p:nth-child(1)")
        self._introduction = pre_intro[0].get_text()

    def _init_catalog(self):
        pre_catalog = self.bs.select("body > div.listmain > dl > dd > a")
        for item in pre_catalog:
            self._book_catalog.append(item.get_text())
            self._catalog_urls.append(self._text_server + item.get("href"))
        self._catalog_num = len(self._book_catalog)

    @staticmethod
    def _beautify_content(content):
        return content

    def run(self, use_proxy):
        print(
            "Book Name: {}\nAuthor: {}\nLast Update Time: {}".format(
                self._book_name, self._author, self._current_time
            )
        )
        self._download_all_content(use_proxy)
        self._make_epub()
