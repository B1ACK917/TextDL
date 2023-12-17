from utils.Crawler.ibCrawler import ibCrawler
from utils.Crawler.qulaCrawler import qulaCrawler
from utils.Crawler.bqg66Crawler import bqg66Crawler
from utils.Crawler.qzfsCrawler import qzfsCrawler
from utils.Crawler.bqgeCrawler import bqgeCrawler
from utils.Func.Src.logger import iprint
from utils.Crawler.epubmaker import EpubMaker
from tqdm import tqdm
import time


def gen_crawler(url):
    support_list = [("ibiquge", ibCrawler),
                    ("qu-la", qulaCrawler),
                    ("biquge66", bqg66Crawler),
                    ("quanzhifashi", qzfsCrawler),
                    ("bqge", bqgeCrawler)]
    for server, crawler_object in support_list:
        if server in url:
            crawler = crawler_object(url.strip())
            crawler.crawl_book_info()
            return crawler
    return None


def run_crawler(crawlers):
    books_list = [crawler.get_book_name() for crawler in crawlers]
    iprint("\nDownload list: {}.\nType enter to continue.".format(books_list))
    interrupt = input()
    if interrupt:
        exit(1)
    for crawler in crawlers:
        try:
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
        except Exception as e:
            continue


def run_auto():
    urls, crawlers = [], []
    print("\nDownload URLs:")
    while True:
        download_url = input()
        if not download_url:
            break
        urls.append(download_url)
    for url in tqdm(urls, ncols=50):
        crawlers.append(gen_crawler(url))
        time.sleep(1)

    run_crawler(crawlers)


if __name__ == "__main__":
    run_auto()
