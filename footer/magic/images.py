import os
import tempfile
import re

from django.template import Template, Context
import cairosvg
from PIL import Image
from io import BytesIO, StringIO


DEFAULT_STYLES = {
    'font_size': '10px',
    'font_family': 'courier',
    'font_color': 'green',
}

def make_svg(context):
    svg_tmpl = Template("""
    <svg xmlns="http://www.w3.org/2000/svg"
      width="500" height="400" viewBox="0 0 500 400">

      <text x="0" y="0" font-family="Verdana" font-size="10" fill="blue" dy="0">
        {{ name }} {{ text }}

        {% for k,v in data %}
            {% if v.items %}
	        <tspan x="0" dy="1.0em">
                    {{ k }}:
                </tspan>
                {% for kk, vv in v.items %}
	            <tspan x="0" dy="1.0em">
                        {{ kk }}: <tspan fill="red" dy="0.0em">{{ vv }}</tspan>
                    </tspan>
                {% endfor %} 
	    {% else %} 
	        <tspan x="0" dy="1.0em">
                    {{ k }}: <tspan fill="red" dy="0.0em">{{ v }}</tspan>
                </tspan>
            {% endif %}
        {% endfor %} 
      </text>
    </svg>
    """.strip())

    svg = svg_tmpl.render(Context({'data': sorted(context.iteritems())}))

    return svg


def write_svg_to_png(svg_raw, outfile):

    cairosvg.svg2png(bytestring=svg_raw, write_to=outfile)

    return outfile


#@TODO python2 unicode compatability method
def inline_text_image(text, outfile, styles={}):

    text = str(text) or "?"
   
    for key, val in DEFAULT_STYLES.items():
        if key not in styles:
            styles[key] = val

    try:
        unit_size = re.findall(
            '\d+', styles.get('font_size', '10px'))[0]
        unit_size = int(unit_size)
    except (IndexError, TypeError) as e:
        unit_size = 10

    width = int((len(text) * unit_size) * 0.60)
    height = int((1 * unit_size) * 1.1)
    print width, height
    text = text.upper()

    svg_tmpl = Template("""
    <svg xmlns="http://www.w3.org/2000/svg"
      width="{{ width }}" height="{{ height }}" viewBox="0 0 {{ width }} {{ height }}">

      <text x="0" y="0" font-family="{{ styles.font_family }}" font-size="{{ styles.font_size }}" fill="{{ styles.font_color }}" dy="0">
          <tspan x="0" dy="1.0em">
              {{ text }}
          </tspan>
      </text>
    </svg>
    """.strip())

    context = {
        'width': width,
        'height': height,
        'styles': styles,
        'text': text}

    svg = svg_tmpl.render(Context(context))

    cairosvg.svg2png(bytestring=svg, write_to=outfile)

    return outfile
    

#@TODO python2 unicode compatability method
def inline_text_animation(text_lines, outfile, styles={}):
    if not hasattr(text_lines, '__iter__'):
        text_lines = [text_lines]

    if not len(text_lines):
        return outfile

    tempfiles = []
    height = 0
    width = 0
    for line in text_lines:
        f = tempfile.NamedTemporaryFile(suffix='.png')
        inline_text_image(line, f, styles)
        tempfiles.append(f)

    frames = []
    for f in tempfiles:
        f.seek(0)
        img = Image.open(f)
        print(f.name, img.width, img.height)

        # Use the greatest width and height we find
        if img.height > height:
            height = img.height
        if img.width > width:
            width = img.width

        # Set the background color to white
        bg = Image.new("RGB", img.size, (255,255,255))
        bg.paste(img, img)
        frames.append(bg)

    for i, img in enumerate(frames):
        # Place each frame on the biggest canvas size we need
        bg = Image.new("RGB", (width, height), (255,255,255))
        bg.paste(img, (0, 0, img.width, img.height))
        frames[i] = bg

    frames[0].save(outfile,
             format='gif',
             #transparency=255,
             save_all=True, 
             append_images=frames[1:],
             loop=0,
             optimize=True,
             duration=500,)

    return outfile
