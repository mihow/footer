#import PIL
import cairosvg
from django.template import Template, Context



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


def inline_text_image(text, outfile, fontsize=12):

    width = int((len(text) * fontsize) * 0.60)
    height = int((1 * fontsize) * 1.1)
    text = text.upper()

    svg_tmpl = Template("""
    <svg xmlns="http://www.w3.org/2000/svg"
      width="{{ width }}" height="{{ height }}" viewBox="0 0 {{ width }} {{ height }}">

      <text x="0" y="0" font-family="monospace" font-size="{{ fontsize }}" fill="green" dy="0">
          <tspan x="0" dy="1.0em">
              {{ text }}
          </tspan>
      </text>
    </svg>
    """.strip())

    context = {
        'width': width,
        'height': height,
        'fontsize': fontsize,
        'text': text}

    svg = svg_tmpl.render(Context(context))

    print(svg)
    cairosvg.svg2png(bytestring=svg, write_to=outfile)

    return outfile
    

