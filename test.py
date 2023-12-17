from utils.Crawler.ibCrawler import ibCrawler
from utils.Crawler.qulaCrawler import qulaCrawler
from utils.Crawler.bqg66Crawler import bqg66Crawler
from utils.Crawler.qzfsCrawler import qzfsCrawler
from utils.Crawler.bqgeCrawler import bqgeCrawler
from utils.Crawler.epubmaker import EpubMaker

if __name__ == "__main__":
    # crawler = ibCrawler("http://www.ibiquge.cc/87795/")
    # crawler = qulaCrawler("https://www.qu-la.com/booktxt/88271007116/")
    # crawler=bqg66Crawler("https://www.biquge66.net/book/10636/")
    crawler = qzfsCrawler("http://www.quanzhifashi.com/novel/77001/")
    crawler.run()
    epub = EpubMaker()
    epub.set_arg(*crawler.get_book())
    epub.run()
