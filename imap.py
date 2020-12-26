#!/usr/bin/env python

import configparser
import ssl
from imapclient import IMAPClient, SEEN
import email
from email.utils import parsedate_tz, mktime_tz
from PIL import Image
import os
import io
import logging

logging.basicConfig(
    format='%(asctime)s - %(levelname)s: %(message)s',
    level=logging.INFO
)

config = configparser.ConfigParser()
config.read('config.ini')

ssl_context = ssl.create_default_context()


def crop(path, input):
    im = Image.open(io.BytesIO(input))
    imgwidth, imgheight = im.size
    upper = im.crop((0, 0, imgwidth, imgheight / 2 - 1))
    lower = im.crop((0, imgheight / 2, imgwidth, imgheight))
    upper.save(os.path.join(path + '-upper.png'))
    lower.save(os.path.join(path + '-lower.png'))


with IMAPClient(config['imap']['host'], ssl_context=ssl_context) as server:
    server.login(config['imap']['user'], config['imap']['passwd'])
    server.select_folder('INBOX')

    messages = server.search('UNSEEN')
    for uid, message_data in server.fetch(messages, 'RFC822').items():
        email_message = email.message_from_bytes(message_data[b'RFC822'])
        for part in email_message.walk():
            if part.get_content_type() == 'image/jpeg':
                print(email_message.get('Message-ID'))
                fileName = str(mktime_tz(parsedate_tz(email_message.get('Date')))) + '_' \
                           + email_message.get('Message-ID').strip()[1:][:-1].split("@")[0] + '.jpg'
                if bool(fileName):
                    filePath = os.path.join('./cards/', fileName)
                    if not os.path.isfile(filePath):
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                crop('./cards/' + fileName, part.get_payload(decode=True))
