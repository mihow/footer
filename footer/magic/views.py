import os
import random
import datetime as dt

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.core.serializers.json import DjangoJSONEncoder
from django.template import Template, Context
from django.views.decorators.cache import never_cache
from django.conf import settings

from footer.magic import images
import yahoo_finance




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

    def get_location(self, request):
        import geoip2.database
        from geoip2.errors import AddressNotFoundError
        # @TODO make more robust method of finding user's real IP
        # https://github.com/mihow/django-ipware
        # ip_address = get_client_ip(request)
        ip_address = request.META['REMOTE_ADDR']
        dbpath = settings.GEOIP_DATABASE_PATH 
        lookup = geoip2.database.Reader(dbpath)
        try:
            resp = lookup.city(ip_address)
            # location_name = resp.most_specific.name
            # print(location_name)
            lookup.close()
            return resp 
        except AddressNotFoundError:
            return None

    # @app.route('/request_data.html')
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
