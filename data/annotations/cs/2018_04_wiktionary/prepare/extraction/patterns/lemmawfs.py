# !usr/bin/env python3
# coding: utf-8

"""Regular expression patterns for extraction word-formation relations."""

regex5 = {
    'cs': [
            r'==={1,} související ==={1,}\n(([\*\#].*\n)*)'
          ],

    'en': [
            r'==={1,}Derived terms==={1,}\n(.*\n)*?(\n|={1,})'
          ],

    'de': [
            r'\{\{Wortbildungen\}\}\n(.*\n)*?(==|\{\{)',
            r'\{\{Verkleinerungsformen\}\}\n(.*\n)*?(==|\{\{)',
            r'\{\{Weibliche Wortformen\}\}\n(.*\n)*?(==|\{\{)',
            r'\{\{Männliche Wortformen\}\}\n(.*\n)*?(==|\{\{)',
            r'\{\{Koseformen\}\}\n(.*\n)*?(==|\{\{)'
          ],

    'fr': [
            r'\|dérivés\}.*\n(.*\n)*?(==)',
            r'\|apparentés.*\n(.*\n)*?(==)',
            r'\|gentilés.*\n(.*\n)*?(==)',
            r'\|composés.*\n(.*\n)*?(==)'
          ],

    'pl': [
            r'\{\{pokrewne\}\}\n\:(.*\n)*?(\{)'
          ],

    # project derinet-connect-family
    'ze': [
            r'==={1,}Derived terms==={1,}\n(.*\n)*?(\n|={1,})'
          ],

    'zd': [
            r'\{\{Wortbildungen\}\}\n(.*\n)*?(==|\{\{)',
            r'\{\{Verkleinerungsformen\}\}\n(.*\n)*?(==|\{\{)',
            r'\{\{Weibliche Wortformen\}\}\n(.*\n)*?(==|\{\{)',
            r'\{\{Männliche Wortformen\}\}\n(.*\n)*?(==|\{\{)',
            r'\{\{Koseformen\}\}\n(.*\n)*?(==|\{\{)'
          ],

    'zf': [
            r'\|dérivés\}.*\n(.*\n)*?(==)',
            r'\|apparentés.*\n(.*\n)*?(==)',
            r'\|gentilés.*\n(.*\n)*?(==)',
            r'\|composés.*\n(.*\n)*?(==)'
          ],

    'zp': [
            r'\{\{pokrewne\}\}\n\:(.*\n)*?(\{)'
          ]
}
