from email.header import decode_header
from email.utils import parseaddr
from datetime import datetime


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        for item in content_type.split(';'):
            item = item.strip()
            if item.startswith('charset'):
                charset = item.split('=')[1]
                break
    return charset


def parse_mail_time(mail_datetime):
    gmt_format = "%a, %d %b %Y %H:%M:%S"
    gmt_format2 = "%d %b %Y %H:%M:%S"
    index = mail_datetime.find(' +0')
    if index > 0:
        mail_datetime = mail_datetime[:index]  # 去掉+0800
    formats = [gmt_format, gmt_format2]
    for ft in formats:
        try:
            mail_datetime = datetime.strptime(mail_datetime, ft)
            return mail_datetime
        except Exception as e:
            pass
    raise Exception("邮件时间格式解析错误")


def parser_email_header(msg):
    subject = decode_str(msg['Subject'])

    from_info, from_address = parseaddr(msg['From'])
    from_name = decode_str(from_info)

    to_info, to_address = parseaddr(msg['To'])
    to_name = decode_str(to_info)
    return subject, from_name, from_address, to_name, to_address


def parse_mail_files(msg):
    for part in msg.walk():
        file_name = part.get_filename()
        if file_name is None:
            continue
        filename = decode_str(file_name)
        data = part.get_payload(decode=True)
        att_file = open('./emailFiles/' + filename, 'wb')
        att_file.write(data)
        att_file.close()
        print("附件：" + filename + "保存成功！")


def parse_mail_content(msg):
    content = ''
    if msg.is_multipart():
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            content += parse_mail_content(part)
    else:
        content_type = msg.get_content_type()
        if content_type == 'text/plain':
            # 纯文本或HTML内容:
            content = msg.get_payload(decode=True)
            # 要检测文本编码:
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            return content
        elif content_type == 'text/html':
            pass
    return content
