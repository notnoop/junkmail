Junkmail is an email document classifier that analyzes the likelihood of
responding to an email.  Currently it provides a playground to test the
features to be extracted from emails.

Required Libraries
---------------------
  * Python >= 2.6
  * nltk >= 2.0
  * sqlalchemy > 0.6.0

On mac you can install the dependencies using MacPorts, or in general via
`easy_install` tool.

How to run
---------------------

1. Download your emails with `downloadmail.py` script

    python -m downloadmail test@gmail.com

The script would prompt you for your gmail password.  The script by default
downloads all the emails dating back to beginning of 2010, and stores them
into `mail.sql` file.

2. Run the analyzer on the file:

    python -m analyze mail.sql

The script would show the most important features in determining which emails
you have replied to so far.

Customizations
--------------------

For now, you can customize the analyzer by specifying which features to
extract in `analyze.features`, the method comes with a sample of feature
extractors; you can build on that.

Also the analyzer uses the `nltk` naive bayes classifier.  Feel free to try
other classifiers as well.

