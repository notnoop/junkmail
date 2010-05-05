#!/usr/bin/env python
import re
import sqlite3
import logging
import email, email.parser
import shlex
import rfc822

import models

FORMAT="%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

import nltk

def parse_addr(email):
    parsed = rfc822.parseaddr(email)[1]
    return parsed.lower().strip() if parsed else "Unknown@example.com"

def features(email):
    features = dict()
    features['from'] = email.sender
    features['list-id'] = email.list_id
    pemail = parse_addr(email.sender)

    features['from-email'] = pemail
    features['from-domain'] = pemail.split('@')[1]

    for label in email.labels_list():
        features['label(%s)' % label] = True

    features['to_length'] = len(email.to_.split(',')) if email.to_ else 0
#    if email.to_:
#        for to_address in email.to_.split(','):
#            features['to(%s)' % parse_addr(to_address)] = True

    return features

def was_answered(email):
    return 'needsReply' if email.answered else 'OK'

def analyze_mail(file, verbose=False):
    all_emails = models.Email.all_emails(file)

    train = [
        (features(email), was_answered(email))
        for email in all_emails]

    classifier = nltk.NaiveBayesClassifier.train(train)
    print classifier.labels()

    classifier.show_most_informative_features(30)

def parse_arguments():
    from optparse import OptionParser
    parser = OptionParser('usage: %prog [options] db-file')
    parser.add_option("-v", "--verbose", dest="verbose",
            default=False, help="verbose")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error('db-file argument is required')

    return {'file': args[0], 'verbose':options.verbose}

if '__main__' == __name__:
    options = parse_arguments()
    analyze_mail(**options)

