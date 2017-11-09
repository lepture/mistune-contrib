# -*- coding:utf-8 -*-
"""
    mistune_contrib.pangu
    ~~~~~~~~~~~~~~~~~~~~~

    Separate CJK characters with latin letters

    :copyright: (c) 2017 by Frost Ming
"""
import re
# borrow from six
import sys
PY2 = sys.version_info[0] == 2
if PY2:
    def u(s):
        return unicode(s.replace(r'\\', r'\\\\'), 'unicode_escape')
else:
    def u(s):
        return s
CJK_RE = (r'\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f'
          r'\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff')
PANGU_RE = re.compile(
    u(r'((?<=[{cjk}])[ \t]*(?=[^\n{cjk}])|(?<=[^\n{cjk}])[ \t]*(?=[{cjk}]))'
      .format(cjk=CJK_RE))
)


class PanguRendererMixin(object):
    """RendereMixin to separate CJK characters with latin letters.

    The renderer will wrap the latin letters with a <span> tag rather than
    adding a hardcoded whitespace, so that user can customize the layout in the
    stylesheet.

    :note: The Mixin should be placed before `Renderer` to override correctly
    :Example:

        input: 中国有13亿人口
        output: 中国有<span class="pangu"></span>13<span class="pangu"></span>亿人口

    From: `vinta's pangu project <https://github.com/vinta/pangu.js>`_
    """
    def text(self, text):
        rv = super(PanguRendererMixin, self).text(text)
        rv = PANGU_RE.sub('<span class="pangu"></span>', rv)
        return rv
