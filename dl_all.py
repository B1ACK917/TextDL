from utils.Crawler.ibCrawler import ibCrawler
from Shinomiya.Src.logger import *
from utils.Crawler.epubmaker import EpubMaker
import time

url_pattern = "http://www.ibiquge.cc/{}/"
book_id_max = 100000
for book_id in range(book_id_max):
    url = url_pattern.format(book_id)
    for i in range(3):
        try:
            iprint("Trying {}".format(url))
            crawler = ibCrawler(url)
            crawler.crawl_book_info()
            iprint(crawler.get_book_name())

            begin_time = time.perf_counter()
            crawler.run()
            total_time = time.perf_counter() - begin_time
            iprint(
                "{} has been downloaded. Elapsed time: {} min,{} s\n".format(
                    crawler.get_book_name(), int(total_time // 60), int(total_time % 60)
                )
            )
            iprint("Begin generating epub...")
            epub = EpubMaker()
            epub.set_arg(*crawler.get_book())
            epub.run()
            iprint("Epub generated")
            break
        except Exception as e:
            print(e)
            continue
