from Spider.Spider import BaseSpider


class qulaSpider(BaseSpider):
    def __init__(self, target):
        super().__init__(r"https://www.qu-la.com", target)
        self._init_others()

    def _init_information(self):
        pre_name = self.bs.select("#list > div.book-main > div.book-text > h1")
        self._book_name = pre_name[0].get_text()
        pre_author = self.bs.select("#list > div.book-main > div.book-text > span")
        self._author = pre_author[0].get_text()[:-2]
        pre_time = self.bs.select("#list > div.block-title > p.update-text > span")
        self._current_time = pre_time[0].get_text()
        pre_intro = self.bs.select("#list > div.book-main > div.book-text > div.intro")
        self._introduction = pre_intro[0].get_text()

    def _init_catalog(self):
        pre_catalog = self.bs.select(
            "#list > div.book-chapter-list > ul:nth-child(4) > li"
        )
        for item in pre_catalog:
            self._book_catalog.append(item.get_text())
            self._catalog_urls.append(
                self._text_server + item.select("a")[0].get("href")
            )
        self._catalog_num = len(self._book_catalog)

    @staticmethod
    def _beautify_content(content):
        content.a.extract()
        content = content
        return content

    def run(self, use_proxy):
        print(
            "Book Name: {}\nAuthor: {}\nLast Update Time: {}".format(
                self._book_name, self._author, self._current_time
            )
        )
        self._download_all_content(use_proxy)
        print("\nFails {} Pages".format(len(self._fails)))
        self._make_epub(True)
