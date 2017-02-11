#import PIL
import cairosvg
from django.template import Template, Context



def make_svg(context):
    svg_tmpl = Template("""
    <svg xmlns="http://www.w3.org/2000/svg"
      width="500" height="600" viewBox="0 0 500 400">

      <text x="0" y="0" font-family="Verdana" font-size="10" fill="blue" dy="0">
        {{ name }} {{ text }}

        {% for k,v in data.items %}
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

    svg = svg_tmpl.render(Context({'data': context}))

    return svg


def write_svg_to_png(svg_raw, outfile):

    cairosvg.svg2png(bytestring=svg_raw, write_to=outfile)

    return outfile
