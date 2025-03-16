import time
import traceback

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from Shinomiya.Src.logger import *
from Shinomiya.Src.path import *
from Shinomiya.Src.threadpool import DarkThreadPool
from utils.Crawler.BaseCrawler.Algo import SequenceRollBack

crawler_logger = create_custom_logger("Crawler", logging.INFO, None, "log/Crawler.log")


class BaseCrawler:
    def __init__(self, server, target) -> None:
        self._server = server
        self._target = target
        self._default_header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        self.__init_params_and_default()

    def __init_params_and_default(self):
        self._init_book_info()
        self._init_book_selector()
        self._init_parameters()
        self._init_utils()

    def _init_book_info(self):
        self._bookname = "Default Bookname"
        self._book_catalog = []
        self._author = "Default Author"
        self._last_update_time = "0-0-0"
        self._intro = "Default"
        self._content_list = []
        self._content_list_AL = []
        self._catalog_urls = []
        self._catalog_num = 0

    def _init_book_selector(self):
        self._catalog_selector = None
        self._bookname_selector = None
        self._author_selector = None
        self._last_update_selector = None
        self._intro_selector = None
        self._content_selector = None

    def _init_parameters(self):
        self._max_retry_count = 4
        self._max_fail_rate = 0.01
        self._max_redownload_times = 2
        self._min_word_num = 5
        self._output_dir = os.path.join("output", "epub")
        check_path(self._output_dir)
        self._encode_type = "UTF-8"
        self._decode_type = "UTF-8"
        self._fails = []
        self._custom_proxy = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        }
        self._use_custom_proxy = False
        self._proxy_pool = "http://127.0.0.1:5555/random"
        self._use_proxy_pool = False
        self._validate_proxy = False
        self._info_crawled = False

    def _init_utils(self):
        self._threadpool = DarkThreadPool(75)
        # self._rollback_method = BinaryRollBack(10)
        self._rollback_method = SequenceRollBack(10)

    def _get_one_random_proxy_from_pool(self):
        proxy = requests.get(self._proxy_pool).text.strip()
        proxies = {"http": "http://" + proxy}
        return proxies

    def _get_proxy_from_pool(self):
        if self._validate_proxy:
            while True:
                try:
                    proxies = self._get_one_random_proxy_from_pool()
                    requests.get(
                        self._target,
                        headers=self._default_header,
                        proxies=proxies,
                        timeout=3,
                    )
                    return proxies
                except Exception as e:
                    crawler_logger.error("validate proxy failed, retry with new proxy.")
                    continue
        else:
            return self._get_one_random_proxy_from_pool()

    @staticmethod
    def _beautify_content(content):
        raise NotImplementedError

    def _check_content(self, content):
        if len(content) < self._min_word_num and "请假" not in content:
            return False
        return True

    def _crawl_homepage(self):
        if self._use_custom_proxy:
            homepage = requests.get(
                self._target, headers=self._default_header, proxies=self._custom_proxy
            )
        elif self._use_proxy_pool:
            proxies = self._get_proxy_from_pool()
            homepage = requests.get(
                self._target, headers=self._default_header, proxies=proxies
            )
        else:
            homepage = requests.get(self._target, headers=self._default_header)
        homepage = homepage.text.encode(homepage.apparent_encoding, "ignore").decode(
            homepage.apparent_encoding, "ignore"
        )
        self._homepage = BeautifulSoup(homepage, "lxml")

    def _crawl_catalog(self):
        catalogs = self._homepage.select(self._catalog_selector)
        for item in catalogs:
            self._book_catalog.append(
                item.get_text().encode(self._encode_type).decode(self._decode_type, errors="ignore"))
            self._catalog_urls.append(self._server + item.get("href"))
        self._catalog_num = len(self._book_catalog)

    def _crawl_information(self):
        bookname = self._homepage.select(self._bookname_selector)
        author = self._homepage.select(self._author_selector)
        last_update = self._homepage.select(self._last_update_selector)
        intro = self._homepage.select(self._intro_selector)
        self._clean_information(bookname, author, last_update, intro)

    def _clean_information(self, bookname, author, last_update, intro):
        self._bookname = (
            bookname[0]
            .get_text()
            .encode(self._encode_type)
            .decode(self._decode_type, "ignore")
            .strip()
        )
        self._author = (
            author[0]
            .get_text()
            .encode(self._encode_type)
            .decode(self._decode_type, "ignore")
            .strip()
        )
        self._last_update_time = (
            last_update[0]
            .get_text()
            .encode(self._encode_type)
            .decode(self._decode_type, "ignore")
            .strip()
        )
        self._intro = (
            intro[0]
            .get_text()
            .encode(self._encode_type)
            .decode(self._decode_type, "ignore")
            .strip()
        )

    def _crawl_content(self, url, index):
        succeed = False
        content = None
        for retry_count in range(1, self._max_retry_count + 1):
            try:
                if self._use_custom_proxy:
                    data = requests.get(
                        url=url,
                        headers=self._default_header,
                        timeout=3,
                        proxies=self._custom_proxy,
                    )
                elif self._use_proxy_pool:
                    proxies = self._get_proxy_from_pool()
                    data = requests.get(
                        url=url,
                        headers=self._default_header,
                        timeout=3,
                        proxies=proxies,
                    )
                else:
                    data = requests.get(
                        url=url, headers=self._default_header, timeout=3
                    )
                html = (
                    data.text.encode(self._encode_type, "ignore")
                    .decode(self._decode_type, "ignore")
                    .replace("\r", "")
                )
                # html = (
                #     data.text.encode(data.apparent_encoding, "ignore")
                #     .decode(data.apparent_encoding, "ignore")
                #     .replace("\r", "")
                # )
                bs = BeautifulSoup(html, "lxml")
                content = bs.select(self._content_selector)[0]
                content = self._beautify_content(content)
                succeed = self._check_content(str(content))
                break
            except Exception as e:
                crawler_logger.error(url)
                crawler_logger.error(traceback.format_exc())
                time.sleep(self._rollback_method.select(retry_count))
        if not succeed:
            self._content_list.append(("", index))
            self._fails.append((url, index))
        else:
            self._content_list.append((str(content), index))
            self._content_list_AL.append((str(content), index))

    def _download(self):
        for i in tqdm(range(self._catalog_num), postfix="Submitting crawling task"):
            url = self._catalog_urls[i]
            self._threadpool.submit(self._crawl_content, url, i)
        while len(self._content_list) != self._catalog_num:
            time.sleep(0.5)
        for i in range(self._max_redownload_times):
            crawler_logger.info("{} pages download failed.".format(len(self._fails)))
            if len(self._fails) < self._max_fail_rate * self._catalog_num:
                crawler_logger.info(
                    "Fail rate lower than max fail rate, finish crawling."
                )
                break
            crawler_logger.info("Redownloading failed pages")
            fails = self._fails.copy()
            self._fails.clear()
            self._content_list = self._content_list_AL.copy()
            for url, i in tqdm(fails, postfix="Resubmitting crawling task"):
                self._threadpool.submit(self._crawl_content, url, i)
            while len(self._content_list) != self._catalog_num:
                time.sleep(0.5)
        self._content_list = sorted(self._content_list, key=lambda x: x[1])

    def _crawl_book_info(self):
        if not self._info_crawled:
            self._crawl_homepage()
            self._crawl_catalog()
            self._crawl_information()
            self._info_crawled = True

    def crawl_book_info(self):
        self._crawl_book_info()

    def run(self):
        self._crawl_book_info()

        crawler_logger.info("Book Name: {}".format(self._bookname))
        crawler_logger.info("Author: {}".format(self._author))
        crawler_logger.info("Last Update Time: {}".format(self._last_update_time))
        self._download()
        self._output = self._bookname + ".epub"
        self._content_list = [i[0] for i in self._content_list]

    def set_proxy(
            self, use_custom_proxy=False, use_proxy_pool=False, validate_proxy=False
    ):
        self._use_custom_proxy = use_custom_proxy
        self._use_proxy_pool = use_proxy_pool
        self._validate_proxy = validate_proxy
        crawler_logger.info(
            "\nuse_custom_proxy: {}, use_proxy_pool: {}, validate_proxy: {}\n".format(
                use_custom_proxy, use_proxy_pool, validate_proxy
            )
        )

    def get_book(self):
        return (
            self._bookname,
            self._author,
            self._intro,
            self._content_list,
            self._book_catalog,
            self._catalog_num,
            self._output_dir,
        )

    def get_book_name(self):
        return self._bookname
