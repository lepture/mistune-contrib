

class TOCMixin(object):
    def header(self, text, level, raw=None):
        if not hasattr(self, 'toc_tree'):
            self.toc_tree = []
            self.toc_count = 0
        rv = '<h%d id="#toc-%d>%s</h%d>\n' % (
            level, self.toc_count, text, level
        )
        self.toc_tree.append((self.toc_count, text, level, raw))
        self.toc_count += 1
        return rv

    def render_toc(self, level=3):
        """Render TOC to HTML.

        :param level: render toc to the given level
        """
        return '\n'.join(self._iter_toc(level))

    def _iter_toc(self, level):
        first_level = None
        last_level = None

        yield '<ul id="table-of-content">'

        for toc in self.toc_tree:
            index, text, l, raw = toc

            if l > level:
                # ignore this level
                continue

            if first_level is None:
                # based on first level
                first_level = l
                last_level = l
                yield '<li><a href="#toc-%d">%s</a></li>' % (index, text)
            elif last_level == l:
                yield '<li><a href="#toc-%d">%s</a></li>' % (index, text)
            elif last_level == l - 1:
                last_level = l
                yield '<li><a href="#toc-%d">%s</a>' % (index, text)
                # a new indention
                yield '<ul>'
            elif last_level == l + 1:
                last_level = l
                yield '<li><a href="#toc-%d">%s</a></li>' % (index, text)
                # close indention
                yield '</ul>'
                yield '</li>'

        yield '</ul>'
