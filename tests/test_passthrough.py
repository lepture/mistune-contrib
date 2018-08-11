from mistune_contrib.passthrough import MarkdownTransformer

SAMPLE = """
# Heading

Some text, with a [link](http://example.com).

* List item 1
* List item 2"""


def test_passthrough():
    mdt = MarkdownTransformer()
    res = mdt.output(SAMPLE)
    assert res == SAMPLE


class LinkModifier(MarkdownTransformer):
    def output_link(self, token):
        return '[[Boo]]'


def test_modify():
    mdt = LinkModifier()
    res = mdt.output(SAMPLE)
    assert '[[Boo]]' in res
    assert 'example.com' not in res
