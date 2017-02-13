from __future__ import print_function

import tempfile
from django.test import TestCase, RequestFactory

import cairosvg



def setup_view(ViewClass, request, *args, **kwargs):
    """Mimic ``as_view()``, but returns view instance.
    Use this function to get view instances on which you can run unit tests,
    by testing specific methods."""

    view_instance = ViewClass()
    view_instance.request = request
    view_instance.args = args
    view_instance.kwargs = kwargs
    return view_instance


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


class VisitorDataTests(TestCase):

    def setUp(self):
        from .views import FooterView
        self.client = RequestFactory()
        self.request = self.client.get('/', REMOTE_ADDR='65.121.85.202')
        self.view = setup_view(FooterView, self.request)
        # self.response = FooterView.as_view()(request)

    def test_location(self):
        location = self.view.get_location()
        self.assertIn("Beaverton", location.city.name)
