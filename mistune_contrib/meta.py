# coding: utf-8

"""
    mistune_contrib.meta
    ~~~~~~~~~~~~~~~~~~~~

    Support Meta features for mistune. Metadata are keywords headers at the
    top of the Markdown text:

        Title: A Metadata DEMO
        Author: Hsiaoming Yang

    :copyright: (c) 2015 by Hsiaoming Yang.
"""


import re


INDENTATION = re.compile(r'\n\s{2,}')
META = re.compile(r'^(\w+):\s*(.*(?:\n\s{2,}.*)*)\n')


def parse(text):
    """Parse the given text into metadata and strip it for a Markdown parser.

    :param text: text to be parsed
    """
    rv = {}
    m = META.match(text)

    while m:
        key = m.group(1)
        value = m.group(2)
        value = INDENTATION.sub('\n', value.strip())
        rv[key] = value
        text = text[len(m.group(0)):]
        m = META.match(text)

    return rv, text
