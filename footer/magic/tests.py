from __future__ import print_function
import tempfile
from django.test import TestCase


import cairosvg

# Create your tests here.

class ImageTests(TestCase):

    def test_make_svg(self):
        from .images import make_svg
        context = {'name': 'test'}
        svg = make_svg(context)
        self.assertTrue( svg.endswith('</svg>') )
        for v in context.values():
            self.assertIn(v, svg)

    def test_write_svg(self):
        from .images import make_svg, write_svg_to_png
        context = {'name': 'test'}
        svg = make_svg(context)
        #f, fname = tempfile.mkstemp(suffix='.svg') @TODO
        fname = '/tmp/test.svg'
        f = open(fname, 'w')
        f = write_svg_to_png(svg, f)
        f.close()

        # Check if file is binary
        file_content = open(fname, 'rb').read()
        self.assertIn(b'\x00', file_content)
