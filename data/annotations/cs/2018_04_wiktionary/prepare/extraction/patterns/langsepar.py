# !usr/bin/env python3
# coding: utf-8

"""Regular expression patterns for languages separator."""

regex2 = {
    'cs': r'((?<!=)== )',
    'en': r'((?<!=)==[A-Z])',
    'de': r'Sprache\|\w+',
    'fr': r'\{\{langue\|\w+',
    'pl': r'\=\=\s\w+',

    # project derinet-connect-family
    'ze': r'((?<!=)==[A-Z])',
    'zd': r'Sprache\|\w+',
    'zf': r'\{\{langue\|\w+',
    'zp': r'\=\=\s\w+'
}
