import sys
from xml.etree.ElementTree import iterparse
from xml.sax.saxutils import XMLGenerator

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

PATH_TAG = '{http://www.w3.org/2000/svg}path'
RECT_TAG = '{http://www.w3.org/2000/svg}rect'
SVG_TAG = '{http://www.w3.org/2000/svg}svg'
SVG_NS = 'http://www.w3.org/2000/svg'


class CombineSVG(object):
    """
    CombineSVG combines multiple SVGa into a single SVG `output` stream.
    Different `layer_name`s are added into a separate SVG layers (`<g>`).
    Empty layers are stripped.

    Note: Only the simplest SVGs with <path> elements are supported (e.g.
    MapServer Cairo SVG output format).
    """

    def __init__(self, output, root_id=None):
        self.first = True
        self.root_id = root_id
        self.out = XMLGenerator(output, 'utf-8')
        self.out.startPrefixMapping(None, SVG_NS)
        self.out.startDocument()
        self.groups = []
        self.actual_groups = []

    def push_group(self, name):
        """
        push_group adds a new SVG layer name to be used for the next SVG sub-document with
        add.
        """
        self.groups.append(name)

    def pop_group(self):
        """
        pop_group removes the last added SVG layer.
        """
        self.groups = self.groups[:-1]

    def balance_group(self):
        """
        balance_group opens/closes <g> tags as necessary.
        We can't create the <g> tags in push/pop_group as we do not want them for empty
        layers.
        """
        for want, got in zip_longest(self.groups, self.actual_groups):
            if want == got:
                continue
            if got is None:
                self.out.startElement('g', {'id': want})
                self.out.characters("\n")
                self.actual_groups.append(want)
                self.balance_group()
                return
            if want is None or want != got:
                self.out.endElement('g')
                self.out.characters("\n")
                self.actual_groups.pop()
                self.balance_group()
                return

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def add(self, r):
        """
        Add an SVG layer with `layer_name` from file object `r`.
        """
        for evt, elem in iterparse(r, events=('start', 'end')):
            if evt == 'start' and self.first and elem.tag == SVG_TAG:
                # copy <svg> from first doc, otherwise ignore
                svg_attrib = {(None, k): v for k, v in elem.attrib.items()}
                if self.root_id:
                    svg_attrib[(None, 'id')] = self.root_id

                self.out.startElementNS((SVG_NS, 'svg'), 'svg', svg_attrib)
                self.out.characters("\n")
                continue

            if evt == 'end' and self.first and elem.tag == RECT_TAG:
                # copy only first <rect>, used by Mapserver to draw blank canvas, but we
                # need all additional to be transparent.
                self.balance_group()
                self.out.startElement('rect', elem.attrib)
                self.out.endElement('rect')
                self.out.characters("\n")

            elif evt == 'end' and elem.tag == PATH_TAG:
                # all drawings are included in <path> tags
                self.balance_group()
                self.out.startElement('path', elem.attrib)
                self.out.endElement('path')
                self.out.characters("\n")

        self.first = False

    def close(self):
        """
        Close all open SVG XML elements.
        """
        self.groups = []
        self.balance_group()

        self.out.endElementNS((SVG_NS, 'svg'), 'svg')
        self.out.endDocument()


if __name__ == '__main__':
    c = CombineSVG(output=sys.stdout)

    for fname in sys.argv[1:]:
        with open(fname, 'rb') as f:
            c.add(fname, f)

    c.close()
