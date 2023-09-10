import time
import logging
import json

from utils.Func.Src.logger import *
from utils.Func.Src.threadpool import DarkThreadPool
from utils.Listener.MailGetter import Getter
from utils.Listener.MailSender import Sender
from utils.Crawler.ibCrawler import ibCrawler
from utils.Crawler.qulaCrawler import qulaCrawler
from utils.Crawler.epubmaker import EpubMaker

mail_logger = create_custom_logger("mailBot", logging.DEBUG, None, "log/mailBot.log")
threadpool = DarkThreadPool(32)


def gen_crawler(url):
    mail_logger.debug("gen_crawler")
    support_list = [("ibiquge", ibCrawler), ("qu-la", qulaCrawler)]
    for server, crawler_object in support_list:
        if server in url:
            crawler = crawler_object(url.strip())
            crawler.crawl_book_info()
            return crawler
    return None


def run_crawler(crawlers, sender: Sender, to_address):
    mail_logger.debug("run_crawler")
    books_list = [crawler.get_book_name() for crawler in crawlers]
    iprint("Download list: {}.\n".format(books_list))
    files, book_names = [], []
    for crawler in crawlers:
        book_names.append(crawler.get_book_name())
    sender.send(
        to_address,
        "开始下载".format(len(crawlers)),
        "书籍列表:\n{}".format("\n".join(book_names)),
        [],
    )
    for crawler in crawlers:
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
        files.append(crawler.get_output_path())
        mail_logger.debug("Assets: {}".format(files))

    sender.send(
        to_address,
        "{}本书下载完成".format(len(crawlers)),
        "书籍列表:\n{}".format("\n".join(book_names)),
        files,
    )


def parse_and_crawl(content, sender, fromer):
    mail_logger.debug("parse_and_crawl")
    crawlers = []
    urls = content.split("\n")
    for url in urls:
        crawler = gen_crawler(url)
        if crawler:
            crawlers.append(crawler)
    threadpool.submit(run_crawler, crawlers, sender, fromer)


def listen(user_, auth_):
    getter = Getter()
    getter.login(user_, auth_)
    sender = Sender()
    sender.login(user_, auth_)

    latest_mail_nums = getter.get_current_mail_nums()
    while True:
        try:
            cur_mail_nums = getter.get_current_mail_nums()
            mail_logger.info(
                "cur: {}, latest:{}".format(cur_mail_nums, latest_mail_nums)
            )
            if cur_mail_nums > latest_mail_nums:
                new_mails = getter.get_new_mails(cur_mail_nums - latest_mail_nums)
                for mail in new_mails:
                    mail_logger.info("{}".format(mail))
                    if mail.is_legal_request():
                        content = mail.get_content()
                        fromer = mail.get_from_address()
                        threadpool.submit(parse_and_crawl, content, sender, fromer)
                latest_mail_nums = cur_mail_nums
            elif cur_mail_nums < latest_mail_nums:
                latest_mail_nums = cur_mail_nums
        except Exception as e:
            mail_logger.error("{}".format(e))
            latest_mail_nums = getter.get_current_mail_nums()
        finally:
            time.sleep(10)


if __name__ == "__main__":
    with open("config/config.json") as config_file:
        config = json.load(config_file)
    user = config["user"]
    auth = config["auth"]
    listen(user, auth)
