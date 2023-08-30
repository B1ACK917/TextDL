from utils.Crawler.ibCrawler import ibCrawler
from utils.Crawler.epubmaker import EpubMaker


if __name__ == "__main__":
    crawler = ibCrawler("http://www.ibiquge.cc/87795/")
    crawler.run()
    epub = EpubMaker()
    epub.set_arg(*crawler.get())
    epub.run()
