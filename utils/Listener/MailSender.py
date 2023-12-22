import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


from Shinomiya.Src.logger import *


class Sender(object):
    def __init__(self):
        self._pop3Address = "pop.qq.com"

    def _connect_smtp(self, show_info=False):
        self._server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        if show_info:
            iprint("Init SMTP Server.")
        self._server.login(self._address, self._authCode)
        if show_info:
            iprint("Logged.")

    def _login(self, address, auth_code, server_port):
        self._address = address
        self._authCode = auth_code
        self._serverPort = server_port
        self._connect_smtp(show_info=True)

    def login(self, address, auth_code, server_port=995):
        assert len(address) > 7 and address[-7:] == "@qq.com", "Invalid Email Address."
        assert len(auth_code) == 16, "Invalid Authentication Code."
        if server_port != 995:
            iprint("Change Default Server Port From 995 to {}".format(server_port))
        self._login(address, auth_code, server_port)

    def send(self, to_address, subject, content, file_path_list):
        self._connect_smtp()
        message = MIMEMultipart()
        message["From"] = "DownLoader <{}>".format(self._address)
        message["Subject"] = Header("{}".format(subject), "utf8").encode()
        message["To"] = "{}".format(to_address)

        attr2 = MIMEText(content, "plain", "utf-8")
        message.attach(attr2)

        for file_path in file_path_list:
            attr = MIMEText(
                open(r"{}".format(file_path), "rb").read(), "base64", "utf-8"
            )
            attr["content_Type"] = "application/octet-stream"
            attr.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.split(file_path)[1],
            )
            message.attach(attr)

        self._server.sendmail(
            self._address, [to_address, self._address], message.as_string()
        )
