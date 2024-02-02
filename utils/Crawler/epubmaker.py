import os

from ebooklib import epub
from tqdm import tqdm


class EpubMaker:
    def __init__(self):
        self.catalog = []
        self.identifier = 'Default'
        self.title = 'Default'
        self.language = 'zh_Hans'
        self.author = 'Default'
        self.toc = []
        self.content = []
        self.nums = 0
        self.book = None
        self.output_path = 'Default'
        self.output_name = 'Default'

    def set_arg(self, title, author, introduction, content, catalog, num, output_path, language='zh_Hans'):
        self.title = title
        self.author = author
        self.book_intro = introduction
        self.language = language
        self.content = content
        self.catalog = catalog
        self.nums = num
        self.output_name = title + '.epub'
        self.output_path = output_path

    def run(self):
        self.book = epub.EpubBook()
        self.book.set_identifier(self.identifier)
        self.book.set_language(self.language)
        self.book.set_title(self.title)
        self.book.add_author(self.author)

        copyright = epub.EpubHtml(title="版权声明", file_name="copyright.html")
        copyright.content = """<h1>版权声明</h1>
        <p>本工具目的是将免费网络在线小说转换成方便kindle用户阅读的epub电子书, 作品版权归原作者或网站所有, 请不要将该工具用于非法用途。</p>
        """
        self.book.add_item(copyright)
        self.toc.append(epub.Link("copyright.html", "版权声明", "copyright"))

        book_intro = epub.EpubHtml(title="书籍介绍", file_name="intro.html")
        book_intro.content = """<h1>书籍介绍</h1>
                <p>{}</p>
                """.format(self.book_intro)
        self.book.add_item(book_intro)
        self.toc.append(epub.Link("intro.html", "书籍介绍", "intro"))
        spine = [copyright, book_intro]

        for i in tqdm(range(self.nums), ncols=50):
            ch_name = self.catalog[i]
            chapter = epub.EpubHtml(
                title=ch_name, file_name='ch{}.html'.format(i))
            chapter.set_content(u"<h1>" + ch_name + u"</h1>" + self.content[i])
            self.book.add_item(chapter)
            self.toc.append(epub.Link('ch{}.html'.format(i), ch_name, ch_name))
            spine.append(chapter)

        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(
            uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

        # add CSS file
        self.book.add_item(nav_css)
        # basic spine
        self.book.spine = spine

        self.book.toc = self.toc
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        epub.write_epub(os.path.join(self.output_path,
                                     self.output_name), self.book)
