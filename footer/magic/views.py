import random
import datetime as dt
import StringIO

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.core.serializers.json import DjangoJSONEncoder
from django.template import Template, Context

from django.views.decorators.cache import never_cache

from PIL import Image, ImageDraw
import yahoo_finance
from footer.magic import images




class JSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        return str(o)


class FooterView(View):

    @never_cache # Sets headers for client as well
    def get(self, request):

        # resp = HttpResponse(self.as_html())
        # resp = JsonResponse(
        #         self.request_data(), 
        #         #safe=False,
        #         encoder=JSONEncoder)

        # img = self.as_image()
        # resp = HttpResponse(content_type='image/jpg')
        # img.save(resp, 'JPEG')

        resp = HttpResponse(content_type='image/png')
        svg = images.make_svg(self.request_data())
        images.write_svg_to_png(svg, resp)
        
        return resp

    def stock_price(self):
        goog = yahoo_finance.Share('GOOG')
        price = goog.get_price()
        date = goog.get_trade_datetime()
        return price, date

    def num_views(self):
        return 0

    def locations(self):
        return ','.join([])

    def cache_buster(self):
        return random.randint(00000000000, 999999999999)

    def request_data(self, summarize=True):
        data = self.request.META
        data.update(self.request.POST)
        data.update(self.request.GET)
        if summarize:
            data = self.summarize(data)
        return data

    def summarize(self, data):
        #@TODO add random background color
        keys_of_interest = [
            "HTTP_USER_AGENT",
            "HTTP_ACCEPT_LANGUAGE",
            "PATH_INFO",
            "HOST",
            "HTTP_REFERER",
            "REFERER",
            "REMOTE_ADDR",
            "X-FORWARDED-FOR",
            "HTTP_X_FORWARDED_FOR",
            "REQUEST_URI",
            "HTTP_ACCEPT",
            "HTTP_COOKIE",

        ]
        summary = {}
        summary['TIMESTAMP'] = dt.datetime.now()
        price, date = self.stock_price()
        summary['GOOG_STOCK_PRICE'] = price
        summary['GOOG_STOCK_PRICE_DATE'] = date 

        if hasattr(data, 'items'):
            for k,v, in data.items():
                if hasattr(v, 'items'):
                    for kk in v:
                        if kk.upper() in keys_of_interest:
                            summary[kk] = v[kk]
                else:
                    if k.upper() in keys_of_interest:
                        summary[k] = data[k]
        return summary
                            
        return data

    def data_to_str(self, data):
        tmpl = Template("""
        {% for k,v in data.items %}{% if v.items %}{{ k }}: 
        {% for kk, vv in v.items %}
        {{ kk }}: {{ vv }}{% endfor %} {% else %} 
        {{ k }}: {{ v }} {% endif %}

        {% endfor %}
        """)
        context = Context({'data': data})
        txt =  tmpl.render(context)
        txt = txt.encode('utf8')
        return txt

    def create_image(self, txt, width=1024, height=2048):
        image = Image.new("RGBA", (width,height), (255,255,255))
        draw = ImageDraw.Draw(image)
        draw.text((10, 0), txt, (0,0,0))

        # img_io = StringIO.StringIO()
        # image.save(img_io, 'jpeg', quality=90)
        # img_io.seek(0)

        return image

#     def serve_image(self, pil_img):
#         img_io = stringio.stringio()
#         pil_img.save(img_io, 'jpeg', quality=90)
#         img_io.seek(0)
#         response = HttpResponse(img_io, mimetype='image/jpeg')
#         # See https://emailexpert.org/gmail-tracking-changes-the-fix-what-you-need-to-know/
#         if 'GoogleImageProxy' in request.headers.get('User-Agent', ''):
#             # This works - we get a request, but we serve a broken image
#             # Can we log the unique request data, and then serve a redirect with a custom 
#             # image?
#             # response.content_length = 0
#             pass
#         return response

    # @app.route('/request_data.jpg')
    # @nocache
    def as_image(self):
        txt = self.data_to_str(self.request_data())
        img = self.create_image(txt) 
        # return self.serve_image(img)
        return img

#    # @app.route('/request_data.html')
    def as_html(self):
        data = self.request_data()
        tmpl = Template("""
        <!doctype html>
        <html><body style="font-family: monospace;">
        <ul>
        {% for k,v in data.items %}
        {% if v.items %}
        <li>{{ k }}: 
        <ul>{% for kk, vv in v.items %}
        <li><b>{{ kk }}:</b> {{ vv }}</li>
        {% endfor %}
        </ul>
        {% else %}
        <li>{{ k }}: {{ v }}</li>
        {% endif %} 
        {% endfor %}
        </ul>
        </body></html>
        """)
        data = {'data': Context(data).flatten()}
        return tmpl.render(Context(data))
#
#
#
    # @app.route('/request_data.json')
    def as_json(self):
        data = self.request_data()
        return JsonResponse(data)
#
#    # @app.route('/')
#    def index(self):
#        return redirect(url_for('embed'))
#
#    # @app.route('/summary.jpg')
#    # @nocache
#    def summary_image(self):
#        txt = data_to_str(summarize(request_data()))
#        img = create_image(txt, height=600) 
#        return serve_image(img)
#
#    # @app.route('/summary.json')
#    def summary(self):
#        data = summarize(request_data())
#        return jsonify(data) 
#
#    # @app.route('/location.jpg')
#    # @app.route('/location-<int:request_id>.jpg')
#    # @nocache
#    def location_image(self, request_id=None):
#        source = SOURCE_CITY
#        destination = get_location(request_data())
#        language = get_client_language()
#        user_agent = request.headers.get('User-Agent')
#        if destination:
#            destination_name = destination.city.name
#        else:
#            destination_name = "Unknown"
#        txt = "{} => {} \r\n{} \r\n{}".format(
#            source, destination_name, language, user_agent)
#        log.info('Serving location image: {}'.format(txt))
#        img = create_image(txt, width=600, height=64) 
#        return serve_image(img)
#
#    # @app.route('/location.json')
#    def location(self):
#        data = get_location(request_data()) 
#        return jsonify(data) 
#
#    # @app.route('/embed')
#    def embed(self):
#        tmpl = """
#        <!doctype html>
#        <html><body style="
#            font-family:monospace; 
#            font-size: medium;
#            width: 40em;
#            border: 1px solid blue;
#            padding: 2%;
#            margin: 4% auto;">
#
#        <h2>Select the image below and paste in your email body:</h2>
#        <p>&nbsp;</p>
#        <div style="text-align:center; background: #eee; width: 80%; margin: 0 auto;">
#        <p>[-- text before image --]<br><br></p>
#        <p>
#        <img src="{{ url_for('location_image', _external=True, request_id=buster1) }}" 
#          title="Request data as image"
#          alt="This should be an image with HTTP headers, etc">
#        </p>
#        <p><br>[-- text after image --]</p>
#        </div>
#        <p>&nbsp;</p>
#
#        <h2>Send a test email:</h2>
#        <form action="/email" method="POST">
#        <p>
#        <input 
#          name="email"
#          type="text" 
#          placeholder="youremail@example.org"
#          style="width:95%" />
#        </p>
#        <p>
#        <input type="submit" value="Send!"> 
#        </p>
#        <p>&nbsp;</p>
#
#        <h2>Or here is html for the image tag you can use:</h2>
#        <p>
#        <input 
#          type="text" 
#          value='<img src="{{ url_for('location_image', request_id=buster2, _external=True) }}">' 
#          style="width:95%" />
#        </p>
#
#        <h2>Links</h2>
#        <ul>
#          <li><a href="{{ url_for('as_html') }}">
#            Show request data as HTML</a></li>
#          <li><a href="{{ url_for('as_json') }}">
#            Show request data as JSON</a></li>
#          <li><a href="{{ url_for('location') }}">
#            Show locaton data as JSON</a></li>
#        </ul>
#        </body></html>
#        """
#        return render_template_string(tmpl, 
#                buster1=cache_buster(), buster2=cache_buster())
#
#
#    def get_client_language(self):
#        lang = request.accept_languages
#        # @TODO convert lang code to something more human friendly
#        return lang
#
#    def get_client_ip(self, request_dict):
#        if os.environ.get('FLASK_DEBUG'):
#            return '73.67.227.118'
#
#        potential_ip_keys = [
#        'HTTP_X_FORWARDED_FOR', 
#        'X_FORWARDED_FOR',
#        'HTTP_CLIENT_IP',
#        'HTTP_X_REAL_IP',
#        'HTTP_X_FORWARDED',
#        'HTTP_X_CLUSTER_CLIENT_IP',
#        'HTTP_FORWARDED_FOR',
#        'HTTP_FORWARDED',
#        'HTTP_VIA',
#        'REMOTE_ADDR', 
#        ]
#
#        ignore_ip_prefixes = [
#        '0.',  # externally non-routable
#        '10.',  # class A private block
#        '169.254.',  # link-local block
#        '172.16.', '172.17.', '172.18.', '172.19.',
#        '172.20.', '172.21.', '172.22.', '172.23.',
#        '172.24.', '172.25.', '172.26.', '172.27.',
#        '172.28.', '172.29.', '172.30.', '172.31.',  # class B private blocks
#        '192.0.2.',  # reserved for documentation and example code
#        '192.168.',  # class C private block
#        '255.255.255.',  # IPv4 broadcast address
#        '2001:db8:',  # reserved for documentation and example code
#        'fc00:',  # IPv6 private block
#        'fe80:',  # link-local unicast
#        'ff00:',  # IPv6 multicast
#        '127.',  # IPv4 loopback device
#        '::1',  # IPv6 loopback device
#        ]
#
#        for key in potential_ip_keys:
#            match = request_dict['environ'].get(key)
#            if match:
#                for prefix in ignore_ip_prefixes:
#                    if match.startswith(prefix):
#                        continue
#                return match
#
#        return None
#
#
#    def get_location(self, request):
#        import geoip2.database
#        from geoip2.errors import AddressNotFoundError
#        # @TODO make more robust method of finding user's real IP
#        # https://github.com/mihow/django-ipware
#        ip_address = get_client_ip(request)
#        dbpath = os.path.join(os.path.dirname(__file__), 'GeoLite2-City.mmdb')
#        lookup = geoip2.database.Reader(dbpath)
#        try:
#            resp = lookup.city(ip_address)
#            # location_name = resp.most_specific.name
#            # print(location_name)
#            lookup.close()
#            return resp 
#        except AddressNotFoundError:
#            return None
#
#
#    def ga_image_url(self, request_id, user_id, debug=True):
#        if debug:
#            base_url = 'https://www.google-analytics.com/debug/collect?v=1'
#        else:
#            base_url = 'https://www.google-analytics.com/collect?v=1'
#
#        url = ('{base_url}'
#               '&tid={ga_id}'
#               '&uid={user_id}'
#               '&cid={request_id}'
#               '&t=event&ec=email&ea=open'
#               '&dp=/email/{request_id}'
#               ''.format(
#                  base_url=base_url,
#                  ga_id=os.environ.get('GOOGLE_ANALYTICS_ID'),
#                  request_id=request_id,
#                  user_id=user_id)
#              )
#
#        return url
#
#    # @app.route('/email', methods=['POST'])
#    def send_email(self):
#        email = request.form['email']
#        body_tmpl = """
#        Hello! Your image is below: <br><br>
#
#        {% autoescape false %}
#        <img src="{{ footer_img_url }}" 
#          alt="Image with your location, etc should be here."><br><br>
#        {% endautoescape %}
#
#        -Footer <br><br>
#
#        {% autoescape false %}
#        <img src="{{ google_image_url }}">
#        {% endautoescape %}
#        """
#
#        request_id = cache_buster()
#        user_id = md5.md5(email).hexdigest()
#
#        debug=os.environ.get('FLASK_DEBUG', False)
#        body = render_template_string(
#                body_tmpl, 
#                footer_img_url=url_for('location_image', 
#                                       request_id=request_id,
#                                       _external=True),
#                google_image_url=ga_image_url(
#                    request_id, 
#                    user_id,
#                    debug=debug))
#
#        body = body.encode('utf8')
#
#        result = ses.send_email(
#        Source='footer@bunsen.town',
#            Destination={
#            'ToAddresses': [
#                email,
#            ],
#            },
#            Message={
#            'Subject': {
#                'Data': 'Footer project test #{}'.format(cache_buster()),
#            },
#            'Body': {
#                #'Text': {
#                #    'Data': 'string',
#                #    'Charset': 'string'
#                #},
#                'Html': {
#                'Data': body,
#                }
#            }
#            },
#        )
#         
#        status_code = result.get('ResponseMetadata').get('HTTPStatusCode')
#        if str(status_code).startswith('2'):
#            return "Success!" 
#        else:
#            return "Something went wrong :("
