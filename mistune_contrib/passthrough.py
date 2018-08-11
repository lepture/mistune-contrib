"""A Markdown passthrough for mistune.

This can be subclassed to easily allow transformations of Markdown.
"""
import inspect
from mistune import Renderer, BlockLexer, InlineLexer, _pre_tags


class RawBlockLexer(BlockLexer):
    def parse(self, text, rules=None):
        text = text.rstrip('\n')

        if not rules:
            rules = self.default_rules

        def manipulate(text):
            for key in rules:
                rule = getattr(self.rules, key)
                m = rule.match(text)
                if not m:
                    continue
                getattr(self, 'parse_%s' % key)(m)
                return m, key
            return False  # pragma: no cover

        n_output_tokens = 0
        raw_tokens = []

        while text:
            ret = manipulate(text)
            if ret is not False:
                m, rule = ret
                tokens = self.tokens[n_output_tokens:]
                n_output_tokens = len(self.tokens)
                raw_tokens.append({'text': m.group(0),
                                   'block': True,
                                   'type': rule,
                                   'tokens': tokens})
                text = text[len(m.group(0)):]
                continue
            if text:  # pragma: no cover
                raise RuntimeError('Infinite loop at: %s' % text)
        return raw_tokens


class RawInlineLexer(InlineLexer):
    def __init__(self, rules=None, **kwargs):
        super(RawInlineLexer, self).__init__(Renderer(), rules=rules, **kwargs)

    def parse(self, text, rules=None):
        if not rules:
            rules = list(self.default_rules)

        if self._in_footnote and 'footnote' in rules:
            rules.remove('footnote')

        def manipulate(text):
            for key in rules:
                pattern = getattr(self.rules, key)
                m = pattern.match(text)
                if not m:
                    continue
                return m, key
            return False  # pragma: no cover

        tokens = []

        while text:
            ret = manipulate(text)
            if ret is not False:
                m, rule = ret
                tokens.append(
                    {'type': rule, 'block': False, 'text': m.group(0)})
                text = text[len(m.group(0)):]
                continue
            if text:  # pragma: no cover
                raise RuntimeError('Infinite loop at: %s' % text)

        return tokens


class MarkdownTransformer(object):
    def __init__(self, inline=None, block=None, **kwargs):
        if inline and inspect.isclass(inline):
            inline = inline(**kwargs)
        if block and inspect.isclass(block):
            block = block(**kwargs)

        if inline:
            self.inline = inline
        else:
            self.inline = RawInlineLexer(**kwargs)

        self.block = block or RawBlockLexer()
        self.footnotes = []
        self.tokens = []

        # detect if it should parse text in block html
        self._parse_block_html = kwargs.get('parse_block_html')

    def pop(self):
        if not self.tokens:
            return None
        self.token = self.tokens.pop()
        return self.token

    def peek(self):
        if self.tokens:
            return self.tokens[-1]
        return None  # pragma: no cover

    def output(self, text, rules=None):
        self.tokens = self.block(text, rules)
        self.tokens.reverse()

        self.inline.setup(self.block.def_links, self.block.def_footnotes)

        results = []
        while self.pop():
            results.append(self.tok())
        return ''.join(results)

    def tok(self):
        t = self.token['type']

        # sepcial cases
        if t.endswith('_start'):
            t = t[:-6]

        return getattr(self, 'output_%s' % t, self.block_default)()

    def inline_tokens(self, text, rules=None):
        results = []
        for t in self.inline.parse(text, rules=rules):
            meth = getattr(self, 'output_'+t['type'], self.inline_default)
            results.append(meth(t))
        return ''.join(results)

    def block_default(self):
        return self.token['text']

    def inline_default(self, token):
        return token['text']

    def tok_text(self):
        text = self.token['text']
        while self.peek()['type'] == 'text':
            text += '\n' + self.pop()['text']
        return self.inline_tokens(text)

    def change_replace(self, raw, fragment, rules=None):
        processed = self.inline_tokens(fragment)
        if processed != fragment:
            return raw.replace(fragment, processed)
        return raw

    def output_heading(self):
        raw = self.token['text']
        text = self.token['tokens'][0]['text']
        return self.change_replace(raw, text)

    def output_table(self):
        token = self.token['tokens'][0]
        raw = self.token['text']

        # header part
        for i, value in enumerate(token['header']):
            raw = self.change_replace(raw, value)

        # body part
        for i, row in enumerate(token['cells']):
            for j, value in enumerate(row):
                raw = self.change_replace(raw, value)

        return raw

    def output_block_quote(self):
        body = ''
        while self.pop()['type'] != 'block_quote_end':
            body += self.tok()
        return body

    def output_list(self):
        body = ''
        while self.pop()['type'] != 'list_end':
            body += self.tok()
        return body

    def output_list_item(self):
        body = ''
        while self.pop()['type'] != 'list_item_end':
            if self.token['type'] == 'text':
                body += self.tok_text()
            else:
                body += self.tok()

        return body

    def output_loose_item(self):
        body = ''
        while self.pop()['type'] != 'list_item_end':
            body += self.tok()
        return body

    def output_footnote(self):
        self.inline._in_footnote = True
        body = ''
        key = self.token['tokens'][0]['key']
        while self.pop()['type'] != 'footnote_end':
            body += self.tok()
        self.footnotes.append({'key': key, 'text': body})
        self.inline._in_footnote = False
        return body

    def output_open_html(self):
        raw = self.token['text']
        text = self.token['tokens'][0]['text']
        tag = self.token['tokens'][0]['tag']
        if self._parse_block_html and tag not in _pre_tags:
            raw = self.change_replace(raw, text,
                                      rules=self.inline.inline_html_rules)

        return raw

    def output_paragraph(self):
        return self.inline_tokens(self.token['text'])

    def output_text(self, token=None):
        if token:
            return token['text']
        return self.tok_text()
