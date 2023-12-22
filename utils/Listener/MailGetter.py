import poplib
from email.parser import Parser
import arrow
from . import MailParser


from Shinomiya.Src.logger import *


class Mail(object):
    def __init__(self, raw_mail):
        self.__autoCode = "AuthTest"
        decoded = b"\r\n".join(raw_mail).decode("utf-8")
        self.__msg = Parser().parsestr(decoded)
        self._parse_mail()

    def _parse_mail(self):
        self._datetime = arrow.get(
            MailParser.parse_mail_time(self.__msg.get("date"))
        ).format("YYYY-MM-DD HH:mm")
        parsed_header = MailParser.parser_email_header(self.__msg)
        (
            self._subject,
            self._from_name,
            self._from_address,
            self._to_name,
            self._to_address,
        ) = parsed_header
        self._content = MailParser.parse_mail_content(self.__msg)

    def get_content(self):
        return self._content

    def get_from_address(self):
        return self._from_address

    def is_legal_request(self):
        return self.__autoCode in self._subject

    def __str__(self):
        return (
            "Time: {}\n"
            "Subject:{}\n"
            "From: {},{}\n"
            "To: {},{}\n"
            "Content:\n{}".format(
                self._datetime,
                self._subject,
                self._from_name,
                self._from_address,
                self._to_name,
                self._to_address,
                self._content,
            )
        )


class Getter(object):
    def __init__(self):
        self._pop3Address = "pop.qq.com"

    def _parse_email_server(self):
        email_server = self._server
        # num, total_size = email_server.stat()
        # self._curMails = num
        resp, mails, octets = email_server.list()
        self._curMails = len(mails)

    def _parse_new_mails(self, mail_nums):
        email_server = self._server
        resp, mails, octets = email_server.list()
        index = len(mails)
        new_mails = []
        for i in range(index, index - mail_nums, -1):
            resp, lines, octets = email_server.retr(i)
            mail = Mail(lines)
            new_mails.append(mail)
        return new_mails

    def _connect_pop3(self, show_info=False):
        self._server = poplib.POP3_SSL(
            host=self._pop3Address, port=self._serverPort, timeout=10
        )
        if show_info:
            iprint("Init Server.")
        self._server.user(self._address)
        if show_info:
            iprint("Set User.")
        self._server.pass_(self._authCode)
        if show_info:
            iprint("Auth.")

    def _login(self, address, auth_code, server_port):
        self._address = address
        self._authCode = auth_code
        self._serverPort = server_port
        self._connect_pop3(show_info=True)
        self._parse_email_server()

    def login(self, address, auth_code, server_port=995):
        assert len(address) > 7 and address[-7:] == "@qq.com", "Invalid Email Address."
        assert len(auth_code) == 16, "Invalid Authentication Code."
        if server_port != 995:
            iprint("Change Default Server Port From 995 to {}".format(server_port))
        self._login(address, auth_code, server_port)

    def get_current_mail_nums(self):
        self._connect_pop3()
        self._parse_email_server()
        return self._curMails

    def get_new_mails(self, last_cnt):
        return self._parse_new_mails(last_cnt)
