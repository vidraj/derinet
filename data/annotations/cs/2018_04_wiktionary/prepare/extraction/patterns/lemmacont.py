# !usr/bin/env python3
# coding: utf-8

"""Regular expression pattern for extraction language content."""

regex3 = {
    'cs': r'== čeština ==\n(.*\n)*?(== )',
    'en': r'==English==\n(.*\n)*?(----)',
    'de': r'Sprache\|Deutsch.*\n(.*\n)*?(== )',
    'fr': r'== \{\{langue\|cs\}\} ==.*\n(.*\n)?(== \{\{langue\|)',
    'pl': r'\{język polski\}.*\n(.*\n)*?(\=\=\s\w+)',

    # project derinet-connect-family
    'ze': r'==Czech==\n(.*\n)*?(----)',
    'zd': r'Sprache\|Tschechisch.*\n(.*\n)*?(== )',
    'zf': r'== \{\{langue\|cs\}\} ==.*\n(.*\n)?(== \{\{langue\|)',
    'zp': r'\{język czeski\}.*\n(.*\n)*?(\=\=\s\w+)'
}
