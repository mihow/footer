import os
import random
import datetime as dt

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.core.serializers.json import DjangoJSONEncoder
from django.template import Template, Context
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.conf import settings
from django.utils import timezone
import pytz

from footer.magic import images
import yahoo_finance
from urllib2 import URLError # @TODO python2 only?
from ipware.ip import get_ip, get_real_ip
import boto3




class JSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        return str(o)

def random_num():
    return random.randint(00000000000, 999999999999)


class InlineTextImage(View):

    @never_cache
    def get(self, request):

        resp = HttpResponse(content_type='image/png')
	# text = self.kwargs.get('text', '?')
	text = request.GET.get('text', '?')
        svg = images.inline_text_image(text, resp)
        
        return resp


class FooterView(TemplateView):
    template_name = 'email.html'

    def location(self):
        loc = self.get_location()
        if loc: 
            return "%s, %s" % (loc.city.name, loc.country.name)
        else:
            return "Unknown"

    def ip(self):
        return self.get_ip()

    def user_agent(self):
        return self.request.META.get('HTTP_USER_AGENT')

    def get_location(self):
        import geoip2.database
        from geoip2.errors import AddressNotFoundError

        ip_address = self.get_ip()
        dbpath = settings.GEOIP_DATABASE_PATH 
        lookup = geoip2.database.Reader(dbpath)
        try:
            resp = lookup.city(ip_address)
            lookup.close()
            return resp 
        except AddressNotFoundError:
            return None

    def get_ip(self):
        real_ip = get_real_ip(self.request)
        if real_ip is not None:
            return real_ip

        # best_ip = get_ip(self.request)
        # if best_ip is not None:
        #     return best_ip

        test_ip = settings.TEST_REMOTE_IP
        if test_ip is not None:
            return test_ip

    def ga_image_url(self):
        if settings.DEBUG:
            base_url = 'https://www.google-analytics.com/debug/collect?v=1'
        else:
            base_url = 'https://www.google-analytics.com/collect?v=1'

        request_id = random_num() # @TODO
        user_id = self.request.session.session_key

        url = ('{base_url}'
               '&tid={ga_id}'
               '&uid={user_id}'
               '&cid={request_id}'
               '&t=event&ec=email&ea=open'
               '&dp=/email/{request_id}'
               ''.format(
                  base_url=base_url,
                  ga_id=settings.GOOGLE_ANALYTICS_ID,
                  request_id=request_id,
                  user_id=user_id)
              )

        return url

    # Allow POSTs so we can use this request inside SendEmailView
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        return super(FooterView, self).render_to_response(context)



class IndexView(FooterView):
    template_name = 'index.html'


class SendEmailView(View):

    def post(self, request):
        to_email = request.POST['email']
        footer_resp = FooterView.as_view()(request)
	footer_resp.render()
        request_id = random_num() #@TODO

        body_tmpl = Template("""
        Hello! Your footer is below: <br><br>

        -Footer <br><br>
        
        ====== <br<br>
        
        {% autoescape off %}
        {{ footer }}
        {% endautoescape %}
        """)

        body = body_tmpl.render(Context({
            'footer': footer_resp.content,
            }))

        subject = 'Footer project test #{}'.format(request_id)
        body = body.encode('utf8')
        from_email = 'footer@bunsen.town'

        if not settings.DEBUG:
            from django.core.mail import send_mail

            result = send_mail(
                subject,
                body,
                from_email,
                [to_email],
                html_message=body)

            if result:
                status_code = 200


        else:
            ses = boto3.client('ses')
            result = ses.send_email(
            Source=from_email,
                Destination={
                'ToAddresses': [
                    to_email,
                ],
                },
                Message={
                'Subject': {
                    'Data': subject,
                },
                'Body': {
                    #'Text': {
                    #    'Data': 'string',
                    #    'Charset': 'string'
                    #},
                    'Html': {
                    'Data': body,
                    }
                }
                },
            )
             
            status_code = result.get('ResponseMetadata').get('HTTPStatusCode')

        if str(status_code).startswith('2'):
            return HttpResponse("Success!", status=status_code)
        else:
            return HttpResponse("Something went wrong :(", status=status_code)


class TestImageView(View):

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
        try:
            goog = yahoo_finance.Share('GOOG')
        except URLError:
            price, date = None, None
        else:
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

        summary['TIMESTAMP_UTC'] = dt.datetime.utcnow()
        price, date = self.stock_price()
        summary['GOOG_STOCK_PRICE'] = price
        summary['GOOG_STOCK_PRICE_DATE'] = date 
        location = self.get_location()
        if location:
            summary['LOCATION_CITY'] = location.city.name
            summary['LOCATION_REGION'] = location.subdivisions.most_specific.name
            summary['LOCATION_COUNTRY'] = location.country.name
            summary['LOCATION_TIME_ZONE'] = location.location.time_zone
            summary['LOCATION_ACCURACY_RADIUS'] = location.location.accuracy_radius
            non_empty_traits = {k: v for k, v in location.traits.__dict__.items() if v}
            summary['LOCATION_TRAITS'] = str(non_empty_traits)

            tz = pytz.timezone(location.location.time_zone)
            timezone.activate(tz)
            #local_time = timezone.localtime(utc_time, tz)
            summary['TIMESTAMP_LOCAL'] = timezone.now()
        else:
            summary['LOCATION'] = 'Unknown'


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

    def get_location(self):
        import geoip2.database
        from geoip2.errors import AddressNotFoundError
        # @TODO make more robust method of finding user's real IP
        # https://github.com/mihow/django-ipware

        # Test IP for local dev
        # ip_address = test_ip or self.request.META['REMOTE_ADDR']
        test_ip = settings.TEST_REMOTE_IP
        real_ip = get_real_ip(self.request)
        best_ip = get_ip(self.request)
        ip_address = real_ip or best_ip or test_ip

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
#
