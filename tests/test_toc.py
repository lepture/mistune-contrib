
import mistune
from mistune_contrib.toc import TocMixin


class TocRenderer(TocMixin, mistune.Renderer):
    pass


text = '''# mistune

mistune is a markdown parser in pure python.

## renderer

renderer can change the result html.

## grammar

mistune is parsed by grammar

### inline grammar

inline things

### block grammar

block things

#### level 4

this level will not be parsed

# contrib

here is the contribution

### invalid

this would not show in toc.

## valid

this would be in toc.
'''

expected = '''
<ul id="table-of-content">
  <li><a href="#toc-0">mistune</a>
    <ul>
      <li><a href="#toc-1">renderer</a></li>
      <li><a href="#toc-2">grammar</a>
        <ul>
          <li><a href="#toc-3">inline grammar</a></li>
          <li><a href="#toc-4">block grammar</a></li>
        </ul>
      </li>
    </ul>
  </li>
  <li><a href="#toc-6">contrib</a>
    <ul>
      <li><a href="#toc-8">valid</a></li>
    </ul>
  </li>
</ul>
'''


def test_toc():
    toc = TocRenderer()
    md = mistune.Markdown(renderer=toc)
    assert 'toc-0' in md.parse(text)
    rv = toc.render_toc(level=3)
    rv = rv.replace('\n', '').replace(' ', '')
    assert rv == expected.replace('\n', '').replace(' ', '')
