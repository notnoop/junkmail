from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
import email, email.parser
import shlex

#engine = create_engine('sqlite:///:memory:', echo=True)
def parse_message(raw):
    parser = email.parser.FeedParser()
    parser.feed(raw)
    return parser.close()


Base = declarative_base()
class Email(Base):
    __tablename__ = 'emails'

    num = Column(Integer, primary_key=True)
    message_id = Column(String)
    thread_id = Column(String)
    labels = Column(String)
    uid = Column(Integer)
    raw_message = Column(Text)
    sender = Column(String)
    to_ = Column(String)
    cc = Column(String)
    subject = Column(String)
    list_id = Column(String)
    in_reply_to = Column(String)
    answered = Column(Boolean)
    attachments = Column(Integer)

    def __init__(self, num, message_id, thread_id, labels,uid, raw_message,
            sender, to_, cc, subject, list_id, in_reply_to, answered,
            attachments):
        self.num = num
        self.message_id = message_id
        self.thread_id = thread_id
        self.labels = labels
        self.uid = uid
        self.raw_message = raw_message
        self.sender = sender
        self.to_ = to_
        self.cc = cc
        self.subject = subject
        self.list_id = list_id
        self.in_reply_to = in_reply_to
        self.answered = answered
        self.attachments = attachments

    def __repr__(self):
        return "<Email('%s', '%s', '%s', '%s')>" % (self.num, self.uid,
                self.sender, self.subject)

    def parsed_message(self):
        return  parse_message(self.raw_message)

    def labels_list(self):
        return shlex.split(str(self.labels))

    @classmethod
    def all_emails(cls, file='mail.sql'):
        session = get_session(file)
        return session.query(Email).all()

def get_session(file='mail.sql'):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:///%s' % file, echo=False)
    session = sessionmaker(bind=engine)()
    return session

