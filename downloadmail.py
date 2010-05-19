import imaplib
import re
import sqlite3
import shlex
import logging
import email, email.parser

FORMAT="%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

labels_re = re.compile("S \((.*)\)")

def parse_message(raw):
    parser = email.parser.FeedParser()
    parser.feed(raw)
    return parser.close()


def email_info(num, M):
    typ, data = M.fetch(num, '(X-GM-THRID X-GM-LABELS UID RFC822)')
    header = data[0][1]

    info = data[0][0].split()
    thrid = info[2]
    labels_str = labels_re.search(data[0][0]).group(1)
    labels = shlex.split(labels_str)
    uid = info[-3]
    parsed = parse_message(header)

    return {'num': num,
            'message_id': parsed['Message-ID'],
            'thread_id':thrid,
            'labels_str': labels_str,
            'labels': labels,
            'uid': uid,
            'raw_message': header,
            # fields
            'sender': parsed['from'],
            'to': parsed['to'],
            'cc': parsed['cc'],
            'subject': parsed['subject'],
            'list_id': parsed['List-ID'],
            'in_reply_to': parsed['In-Reply-To'],

            # private
            'answered': False, 'attachments':0, 'to_me':False}

def store_info(info, c):
    try:
        c.execute("""
    insert into emails values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);""",
    (info['num'],info['message_id'],info['thread_id'], info['labels_str'],
        info['uid'], info['raw_message'], info['sender'], info['to'],
        info['cc'], info['subject'], info['list_id'], info['in_reply_to'],
        info['answered'], info['attachments'],info['to_me']))
        c.commit()
    except :
        logging.debug("Error while processing email: thread_id(%s), uid(%s)" %
                (info['thread_id'], info['uid'],))

def download_all_mail(email, password, file):

    # IMAP Initializations
    M = imaplib.IMAP4_SSL("imap.gmail.com")
    M.login(email, password)
    M.select('[Gmail]/All Mail')

    # SQLite Initializations
    c = sqlite3.connect(file)
    c.execute("""create table emails
    (num INTEGER UNIQUE, message_id, thread_id, labels, uid, raw_message,
    sender, to_, cc, subject, list_id, in_reply_to, answered, attachments,
    to_me);""")

    typ, data = M.search(None, 'SINCE', '01-JAN-2010')
    nums = data[0].split()

    total = len(nums)
    counter = 0

    for num in reversed(nums):
        info = email_info(num, M)
        store_info(info, c)
        counter += 1
        logging.debug("Processed %d -- %d to go" % (counter, total - counter))

    M.logout()

    # Set the answered flag
    c.execute("""UPDATE emails
    SET answered = 1
    WHERE message_id IN
      (SELECT in_reply_to FROM emails
       WHERE in_reply_to != '' AND labels like '%Sent%');""")

def parse_arguments():
    from optparse import OptionParser
    import getpass
    parser = OptionParser('usage: %prog [options] gmail-username')
    parser.add_option("-f", "--file", dest="file", default="emails.sql",
            help="destination database file [default: %default]")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error('email argument is required')
    password = getpass.getpass('Password: ')

    return {'email':args[0], 'password':password, 'file':options.file}


if '__main__' == __name__:
    options = parse_arguments()
    download_all_mail(**options)

