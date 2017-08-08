# -*- coding: utf-8 -*-

"""Contains a TreeBuilder subclass for building svg documents: SVGBuilder."""

from datetime import datetime
import math
import xml.etree.ElementTree as ET


def _fix_attrs(**kwargs):
    """Convert keyword arguments to a dictionary of attribute with string
    values. In particular, underscores are replaced with dashes so that xml
    attributes such as stroke-width can be specifed as stroke_width.

    """
    attrs = dict()
    for key, value in kwargs.items():
        attrs[key.replace('_', '-')] = str(value)
    return attrs


class _SVGGroup:
    """A helper class for closing group (and similar) tags automatically by
    using instances of this class as contexts.

    """

    def __init__(self, builder, tag):
        self.builder = builder
        self.tag = tag

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.builder.end(self.tag)


class SVGBuilder(ET.TreeBuilder):
    """A subclass of xml.etree.ElementTree.TreeBuilder with added methods for
    greatly simplifying the creating of svg files.

    Note that this class is still subject to change and needs refinement.

    """

    def __init__(self, width=None, height=None, **kwargs):
        super().__init__()
        attrs = _fix_attrs(xmlns='http://www.w3.org/2000/svg', version='1.1',
                           **kwargs)
        if width is not None:
            attrs['width'] = str(width)
        if height is not None:
            attrs['height'] = str(height)
        self.svg = self.start('svg', attrs)
        self.svg.append(ET.Comment('vbl-stats svg generated at ' +
                                   datetime.today().isoformat()))

    def circle(self, cx, cy, r, **kwargs):
        self.item('circle', cx=cx, cy=cy, r=r, **kwargs)

    def circle_sector(self, cx, cy, r, alpha, theta, **kwargs):
        d = 'M%f,%f L%f,%f A%f,%f 0 %d,%d %f,%f Z' % \
            (cx, cy,
            cx + r * math.cos(alpha),
            cy + r * math.sin(alpha),
            r, r,
            1 if abs(theta) > math.pi else 0,
            1 if theta > 0 else 0,
            cx + r * math.cos(alpha + theta),
            cy + r * math.sin(alpha + theta))
        self.item('path', d=d, **kwargs)

    def defs(self):
        self.start('defs')
        return _SVGGroup(self, 'defs')

    def g(self, **kwargs):
        self.start('g', _fix_attrs(**kwargs))
        return _SVGGroup(self, 'g')

    def item(self, tag, **kwargs):
        self.start(tag, _fix_attrs(**kwargs))
        self.end(tag)

    def line(self, x1, y1, x2, y2, **kwargs):
        self.item('line', x1=x1, y1=y1, x2=x2, y2=y2, **kwargs)

    def rect(self, x, y, w, h, **kwargs):
        self.item('rect', x=x, y=y, width=w, height=h, **kwargs)

    def text(self, text, x, y, **kwargs):
        self.start('text', _fix_attrs(x=x, y=y, **kwargs))
        self.data(text)
        self.end('text')

    def text_group(self, x, y, **kwargs):
        self.start('text', _fix_attrs(x=x, y=y, **kwargs))
        return _SVGGroup(self, 'text')

    def write(self, file_or_name, encoding='UTF-8', xml_decl=True):
        print('Writing SVG to', file_or_name)
        self.end('svg')
        data = self.close()
        tree = ET.ElementTree(data)
        tree.write(file_or_name, encoding, xml_decl)
