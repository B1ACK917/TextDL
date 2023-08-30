from utils.Crawler.ibCrawler import ibCrawler
from utils.Crawler.qulaCrawler import qulaCrawler
from utils.Crawler.epubmaker import EpubMaker


if __name__ == "__main__":
    # crawler = ibCrawler("http://www.ibiquge.cc/87795/")
    crawler = qulaCrawler("https://www.qu-la.com/booktxt/88271007116/")
    crawler.run()
    epub = EpubMaker()
    epub.set_arg(*crawler.get_book())
    epub.run()
