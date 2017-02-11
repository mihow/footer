#import PIL
import cairosvg
from django.template import Template, Context



def make_svg(context):
    svg_tmpl = Template("""
    <?xml version="1.0" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
      "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg width="5cm" height="4cm" version="1.1"
	 xmlns="http://www.w3.org/2000/svg">
      <desc>Four separate rectangles - "{{ name }}"
      </desc>
	<rect x="0.5cm" y="0.5cm" width="2cm" height="1cm"/>
	<rect x="0.5cm" y="2cm" width="1cm" height="1.5cm"/>
	<rect x="3cm" y="0.5cm" width="1.5cm" height="2cm"/>
	<rect x="3.5cm" y="3cm" width="1cm" height="0.5cm"/>

      <!-- Show outline of canvas using 'rect' element -->
      <rect x=".01cm" y=".01cm" width="4.98cm" height="3.98cm"
	    fill="none" stroke="blue" stroke-width=".02cm" />

    </svg>
    """.strip())

    svg = svg_tmpl.render(Context(context))

    return svg


def write_svg_to_png(svg_raw, outfile):

    cairosvg.svg2png(bytestring=svg_raw, write_to=outfile)

    return outfile
