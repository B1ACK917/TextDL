from utils.Crawler.XBiqugeSpider import XBiqugeSpider
from tqdm import tqdm
import time


def gen_spider(url, spe_server=None):
    support_list = [("ibiquge", XBiqugeSpider)]
    for server, spider_object in support_list:
        if server in url:
            return spider_object(url.strip())
    return None


def run_spider(spiders, use_proxy):
    books_list = [spider.get_book_name() for spider in spiders]
    print("\nDownload list: {}.\nType enter to continue.".format(books_list))
    interrupt = input()
    if interrupt:
        exit(1)
    for spider in spiders:
        try:
            begin_time = time.perf_counter()
            spider.run(use_proxy)
            total_time = time.perf_counter() - begin_time
            print(
                "{} has been downloaded. Elapsed time: {} min,{} s\n".format(
                    spider.get_book_name(), int(total_time // 60), int(total_time % 60)
                )
            )
            time.sleep(4)
        except:
            continue


def run_auto():
    urls, spiders = [], []
    use_proxy = False
    print("\nDownload URLs:")
    while True:
        download_url = input()
        if not download_url:
            break
        urls.append(download_url)
    for url in tqdm(urls, ncols=50):
        spiders.append(gen_spider(url))
        time.sleep(1)

    run_spider(spiders, use_proxy)

if __name__ == "__main__":
    run_auto()
