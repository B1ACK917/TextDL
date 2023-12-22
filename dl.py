from utils.Crawler.ibCrawler import ibCrawler
from utils.Crawler.qulaCrawler import qulaCrawler
from utils.Crawler.bqg66Crawler import bqg66Crawler
from utils.Crawler.qzfsCrawler import qzfsCrawler
from utils.Crawler.bqgeCrawler import bqgeCrawler
from Shinomiya.Src.logger import iprint
from utils.Crawler.epubmaker import EpubMaker
from tqdm import tqdm
import time
import argparse

parser = argparse.ArgumentParser(description="Parser")
parser.add_argument("-p", "--proxy", action="store_true", help="custom proxy")
parser.add_argument("-o", "--proxypool", action="store_true", help="use proxypool")
parser.add_argument("-v", "--validate", action="store_true", help="validate proxy")


def gen_crawler(url, use_custom_proxy, use_proxy_pool, validate_proxy):
    support_list = [
        ("ibiquge", ibCrawler),
        ("qu-la", qulaCrawler),
        ("biquge66", bqg66Crawler),
        ("quanzhifashi", qzfsCrawler),
        ("bqge", bqgeCrawler),
    ]
    for server, crawler_object in support_list:
        if server in url:
            crawler = crawler_object(url.strip())
            crawler.set_proxy(use_custom_proxy, use_proxy_pool, validate_proxy)
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


def run_auto(use_custom_proxy, use_proxy_pool, validate_proxy):
    urls, crawlers = [], []
    print("\nDownload URLs:")
    while True:
        download_url = input()
        if not download_url:
            break
        urls.append(download_url)
    for url in tqdm(urls, ncols=50):
        crawlers.append(gen_crawler(url, use_custom_proxy, use_proxy_pool, validate_proxy))
        time.sleep(1)

    run_crawler(crawlers)


if __name__ == "__main__":
    args = parser.parse_args()
    run_auto(args.proxy, args.proxypool, args.validate)
