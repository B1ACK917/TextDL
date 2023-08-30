from bs4 import BeautifulSoup
import requests
import os
import time
import threading
import random

from Func.logger import *


class BaseSpider:
    def __init__(self, server, target):
        self._text_server = server
        self._target = target
        self._default_header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/75.0.3770.80 Safari/537.36",
        }
        self._init_parameters()
        self._init_log()

    def _binary_goback(self, cnt):
        return random.randint(1, self._time_slot_list[cnt] + 1)

    def _init_log(self):
        myapp = logging.getLogger()
        myapp.setLevel(level=logging.ERROR)
        formatter = logging.Formatter(
            "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
        )
        rotatingHandler = logging.handlers.RotatingFileHandler(
            "log/spider.log", maxBytes=5 * 1024 * 1024, backupCount=2, encoding="utf-8"
        )
        rotatingHandler.setFormatter(formatter)
        myapp.addHandler(rotatingHandler)
        logging.debug("Start of program")

    def _init_others(self):
        self._init_homepage()
        self._init_information()
        self._init_catalog()

    def _init_parameters(self):
        self._book_name = "Default"
        self._book_catalog = []
        self._author = "Default"
        self._current_time = "0-0-0"
        self._introduction = "Default"
        self._content_list = []
        self._content_list_AL = []
        self._catalog_urls = []
        self._catalog_num = 0
        self._max_threads = 75
        self._cur_threads = 0
        self._max_retry_count = 4
        self._max_fail_rate = 0.01
        self._min_word_num = 5
        self._output_dir = os.path.join("output", "epub")
        self._abs_path = "/Users/cyberdz/杂货/textDownloader/"
        self._abs_output_dir = "/Users/cyberdz/杂货/textDownloader/output/epub"
        self._time_slot_list = [2**i for i in range(1, 5)]
        self._decode_type = "utf-8"
        self._fails = []
        self._text_tag = "#txt"
        self._clash_proxy = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        }
        self._need_show_progress = True

    def _init_homepage(self):
        # proxies = {
        #     "http": "http://127.0.0.1:1080",
        # }
        # self._target_book_home = requests.get(url=self._target, proxies=proxies)
        self._target_book_home = requests.get(
            url=self._target, headers=self._default_header
        )
        self.html = self._target_book_home.text.encode(
            self._target_book_home.apparent_encoding, "ignore"
        ).decode(self._target_book_home.apparent_encoding, "ignore")
        self.bs = BeautifulSoup(self.html, "lxml")

    def _init_catalog(self):
        pre_catalog = self.bs.select("#list > dl > dd > a")
        for item in pre_catalog:
            self._book_catalog.append(item.get_text())
            self._catalog_urls.append(self._text_server + item.get("href"))
        self._catalog_num = len(self._book_catalog)
        # print(len(self._book_catalog) == len(self._catalog_urls), len(self._book_catalog))

    def _init_information(self):
        pre_name = self.bs.select("#info > h1")
        self._book_name = pre_name[0].get_text()
        pre_author = self.bs.select("#info > p:nth-child(2)")
        self._author = pre_author[0].get_text()[7:]
        pre_time = self.bs.select("#info > p:nth-child(4)")
        self._current_time = pre_time[0].get_text()[5:]
        pre_intro = self.bs.select("#intro > p:nth-child(2)")
        self._introduction = pre_intro[0].get_text()[5:]

    @staticmethod
    def _fork(*args, **kwargs):
        t = threading.Thread(**kwargs)
        t.setDaemon(True)
        t.start()

    @staticmethod
    def _beautify_content(content):
        raise NotImplementedError

    def _check_content(self, content):
        if len(content) < self._min_word_num and "请假" not in content:
            return False
        return True

    def _get_precontent_with_proxy(self, url, index):
        proxy = ProxyFunction.get_proxy().get("proxy")
        succeed = False
        pre_content = None
        for retry_count in range(self._max_retry_count - 1, 0, -1):
            try:
                data = requests.get(
                    url=url,
                    headers=self._default_header,
                    proxies={"http": "http://{}".format(proxy)},
                    timeout=3,
                )
                html = (
                    data.text.encode(data.apparent_encoding, "ignore")
                    .decode(data.apparent_encoding, "ignore")
                    .replace("\r", "")
                )
                bs = BeautifulSoup(html, "lxml")
                pre_content = bs.select(self._text_tag)[0]
                pre_content = self._beautify_content(pre_content)
                succeed = self._check_content(str(pre_content))
                break
            except Exception as e:
                logging.error("{}".format(e))
                if retry_count % self._max_retry_count == 0:
                    proxy = ProxyFunction.get_proxy().get("proxy")
                time.sleep(4)
        if not succeed:
            self._content_list.append(("", index))
            self._fails.append((url, index))
        else:
            self._content_list.append((str(pre_content), index))
            self._content_list_AL.append((str(pre_content), index))
        self._cur_threads -= 1

    def _get_precontent_without_proxy(self, url, index):
        succeed = False
        pre_content = None
        for retry_count in range(self._max_retry_count, 0, -1):
            try:
                # data = requests.get(
                #     url=url, headers=self._default_header, timeout=3, proxies=self._clash_proxy)

                data = requests.get(url=url, headers=self._default_header, timeout=3)
                html = (
                    data.text.encode(data.apparent_encoding, "ignore")
                    .decode(data.apparent_encoding, "ignore")
                    .replace("\r", "")
                )
                # html = data.text.encode('utf-8', 'ignore').decode('utf-8', 'ignore').replace('\r', '')
                bs = BeautifulSoup(html, "lxml")
                pre_content = bs.select(self._text_tag)[0]
                pre_content = self._beautify_content(pre_content)
                succeed = self._check_content(str(pre_content))
                break
            except Exception as e:
                logging.error("{}".format(e))
                time.sleep(self._binary_goback(retry_count % self._max_retry_count))
        if not succeed:
            self._content_list.append(("", index))
            self._fails.append((url, index))
        else:
            self._content_list.append((str(pre_content), index))
            self._content_list_AL.append((str(pre_content), index))
        self._cur_threads -= 1

    def _get_content(self, use_proxy):
        for i in range(self._catalog_num):
            while True:
                if self._cur_threads < self._max_threads:
                    url = self._catalog_urls[i]
                    if use_proxy:
                        self._fork(
                            target=self._get_precontent_with_proxy, args=(url, i)
                        )
                    else:
                        self._fork(
                            target=self._get_precontent_without_proxy, args=(url, i)
                        )
                    self._cur_threads += 1
                    break
                else:
                    time.sleep(3)
        while len(self._content_list) != self._catalog_num:
            time.sleep(1)
        while True:
            if len(self._fails) < self._max_fail_rate * self._catalog_num:
                break
            print(
                "\nFailed to Download {} Pages, Redownloading...\n".format(
                    len(self._fails)
                )
            )
            fails = self._fails.copy()
            self._fails.clear()
            self._content_list = self._content_list_AL.copy()
            for arg in fails:
                while True:
                    if self._cur_threads < self._max_threads:
                        self._fork(target=self._get_precontent_without_proxy, args=arg)
                        self._cur_threads += 1
                        break
                    else:
                        time.sleep(3)
        self._content_list = sorted(self._content_list, key=lambda x: x[1])
        self._need_show_progress = False

    def _show_progress(self):
        while True:
            if self._need_show_progress and (
                len(self._content_list) < self._catalog_num
                or len(self._content_list_AL) < self._catalog_num
            ):
                print(
                    "\rDownloading... {}/{} has been downloaded.      "
                    "Threads Pool: {}/{}".format(
                        len(self._content_list),
                        self._catalog_num,
                        self._cur_threads,
                        self._max_threads,
                    ),
                    end="",
                    flush=True,
                )
                time.sleep(1)
            else:
                print("\rDownloading completed", flush=True)
                break

    def _check_download_dir(self):
        if not os.path.exists("output"):
            os.mkdir("output")

        if not os.path.exists(self._output_dir):
            os.mkdir(self._output_dir)

    def _make_epub(self, save=False):
        epub = epubmaker.EpubMaker()
        epub.set_arg(
            self._book_name,
            self._author,
            self._introduction,
            self._content_list,
            self._book_catalog,
            self._catalog_num,
            self._output_dir,
        )
        epub.run()
        if save:
            np.savez(
                "output/temp/{}.npz".format(self._book_name),
                book_name=self._book_name,
                author=self._author,
                intro=self._introduction,
                content_list=self._content_list,
                book_catalog=self._book_catalog,
                catalog_num=self._catalog_num,
                output_dir=os.path.join("output", "temp"),
            )

    def _trans_mobi(self):
        kindlegen = os.path.join(self._abs_path, "kindlegen")
        in_epub = os.path.join(self._abs_output_dir, self._book_name + ".epub")
        out_mobi = os.path.join(self._abs_output_dir, "..", "mobi", self._book_name)
        print(os.popen("{} {}".format(kindlegen, in_epub)).read())

    def _download_all_content(self, use_proxy=True):
        self._fork(target=self._show_progress)

        self._get_content(use_proxy)
        self._output = self._book_name + ".epub"
        self._check_download_dir()
        self._content_list = [i[0] for i in self._content_list]

    def get_book_name(self):
        return self._book_name

    def get_catalog(self):
        return self._book_catalog, self._catalog_urls

    def get_output_path(self):
        return os.path.join(self._output_dir, self._output)
