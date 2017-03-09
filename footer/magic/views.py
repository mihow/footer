import os
import random
import datetime as dt
import json
from urllib import urlencode

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.core.serializers.json import DjangoJSONEncoder
from django.template import Template, Context
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.conf import settings
from django.utils import timezone
import pytz

from footer.magic import images
from footer.magic import models
import yahoo_finance
from urllib2 import URLError # @TODO python2 only?
from ipware.ip import get_ip, get_real_ip
import boto3




class JSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        return str(o)

def random_num():
    return random.randint(00000000000, 999999999999)

DATE_FORMAT = '%Y-%-m-%-d %-H:%-M %p %Z'

# class FooterRequestView(View):
class FooterRequest(View):
    is_leader = False
    _location = None

    def dispatch(self, request, *args, **kwargs):
        # Save request record to database

        request_data = dict(request.META)
        # is_leader = True if request.GET.get('leader') else False

        # Convert non-serializable values to strings:
        request_data_safe = json.loads(json.dumps(request_data, default=str))
        if self.is_leader:
            # Do we need to save any other requests?
            self.footer = models.FooterRequest.objects.create(
                is_leader=self.is_leader,
                request_data=request_data_safe,
                location=self.get_location(serialize=True),
                user_agent=self.user_agent(),
                ip_address=self.ip(),
            )

        return super(FooterRequest, self).dispatch(request, *args, **kwargs)

    def _past_requests(self):
        # @TODO make this a QueryManager method
        return models.FooterRequest.objects.filter(is_leader=True).filter(
                request_data__QUERY_STRING__contains=('start'))

    def history_animation(self):
        requests = self._past_requests().order_by('ip_address', '-created').distinct('ip_address')
        data = []
        for r in requests:
            tz_name= r.location.get('time_zone')
            if tz_name:
                tz = pytz.timezone(tz_name)
                timestamp = r.created.astimezone(tz)
            else:
                timestamp = r.created

            data.append(", ".join([
                timestamp.strftime(DATE_FORMAT), 
                r.ip_address,
                r.location_str()
            ]))
        return data

    def timestamp(self):
        # @TODO still not working?
	dt_now = timezone.now()
        location = self.get_location()
	if location:
	    tz = pytz.timezone(location.location.time_zone)
	    timezone.activate(tz)
            dt_now = dt_now.astimezone(tz)
        return dt_now.strftime(DATE_FORMAT)

    def timezone(self):
        location = self.get_location()
	if location:
	    tz = pytz.timezone(location.location.time_zone)
	    return tz
	else:
	    return "Unknown"

    def request_count(self):
        return self._past_requests().count()

    def request_count_today(self):
        today_start = self.timestamp().replace(hour=0,minute=0,second=0,microsecond=0)
        return self._past_requests().filter(
		created__gte=today_start).count()

    def request_count_now(self):
        this_minute = self.timestamp().replace(second=0,microsecond=0)
        return self._past_requests().filter(
		created__gte=this_minute).count()

    def location(self):
        # @TODO move all these methods to the model
	# @TODO make location a model field
        # @TODO @IMPORTANT add exception handling here
        loc = self.get_location()
        loc_parts = [loc.city.name, 
                     loc.subdivisions.most_specific.name, 
                     loc.country.name]
        loc_str = '/'.join([p for p in loc_parts if p])
        if loc: 
            return "%s, %s" % (loc_str, self.ip())
        else:
            return "Unknown"

    def location_accuracy(self):
        location = self.get_location()
	if location:
            return location.location.accuracy_radius
        return "Unknown"

    def sender_location(self):
	return "99 Gansevoort St, New York, NY 10014, USA"

    def ip(self):
        return self.get_ip()

    def user_agent(self):
        return self.request.META.get('HTTP_USER_AGENT')

    def user_agent_animation(self):
        agent = self.request.META.get('HTTP_USER_AGENT')
        # @TODO split actual parts using regex 
        agent_parts = [p.strip() for p in agent.split(') ')]
        return agent_parts

    def get_location(self, serialize=False):
        if self._location:
	    return self._location

        import geoip2.database
        from geoip2.errors import AddressNotFoundError

        ip_address = self.get_ip()
        dbpath = settings.GEOIP_DATABASE_PATH 
        lookup = geoip2.database.Reader(dbpath)
        try:
            resp = lookup.city(ip_address)
            lookup.close()
	    self._location = resp 
            if serialize:
                data = {
                    'city': resp.city.name,
                    'location': resp.location.__dict__,
                    'region': resp.subdivisions.most_specific.name,
                    'country': resp.country.name,
                    'time_zone': resp.location.time_zone,
                }
                # Create JSON safe dict
                data = json.loads(json.dumps(data, default=str))
                return data
            else:
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
        base_url = 'https://www.google-analytics.com/collect'

        # if settings.DEBUG:
        #     base_url = 'https://www.google-analytics.com/debug/collect'

        # request_id = random_num() # 
        # user_id = self.request.session.session_key # No sessions

        ga_id = settings.GOOGLE_ANALYTICS_ID
        user_id = settings.GOOGLE_ANALYTICS_USER_VERSION

        params = (
           ('v', 1),
           ('tid', ga_id),
           ('uid', user_id),
           ('t',   'event'),
           ('ec',  'footer'),
           ('ea',  'view'),
           ('el',  user_id),
           ('dp',  '/email/%s' % user_id),
           ('dt',  'Email with Footer #%s' % user_id),
           ('cm',  'email'),
           ('ci',  user_id),
           ('sc',  'start'), # Start a new session every time
        )

        url = "%s?%s" % (base_url, urlencode(params))

        return url

    def styles(self):
        return {
            'font_family': 'courier',
            'font_size': '12px',
            #'font_color': '#000000',
            'font_color': '#000000',
        }


class FooterEmailInstance(FooterRequest, TemplateView):
    template_name = 'email.html'


class IndexView(FooterEmailInstance):
    template_name = 'index.html'


class InlineTextImage(FooterRequest):

    @never_cache
    def get(self, request, param):

        resp = HttpResponse(content_type='image/png')
	if not hasattr(self, param):
	    value = "Not Implemented."
	else:
	    try:
		value = "%s." % getattr(self, param)()
	    except AttributeError as e:
	        #log.error(e)
	        value = "Unavailable (%s)." % e
        svg = images.inline_text_image(value, resp, styles=self.styles())
        
        return resp


class InlineTextAnimation(FooterRequest):

    @never_cache
    def get(self, request, param):

        resp = HttpResponse(content_type='image/gif')
	if not hasattr(self, param):
	    value = "Not Implemented."
	else:
	    try:
		value_list = ["%s." % v for v in getattr(self, param)()]
	    except AttributeError as e:
	        #log.error(e)
	        value_list = ["Unavailable.", e]

        images.inline_text_animation(value_list, resp, styles=self.styles())
        
        return resp


class LeaderImageView(FooterRequest):

    def __init__(self, *args, **kwargs):
        self.is_leader = True
        super(FooterRequest, self).__init__(*args, **kwargs)

    @never_cache
    def get(self, request):

        resp = HttpResponse(content_type='image/gif')
        if self.is_leader:
            if 'start' in request.GET:
                text = "[LEADER START]"
            elif 'end' in request.GET:
                text = "[LEADER END]"
            else: 
                text = "[LEADER ORPHAN!]"
        else:
            text = "[LEADER FAILED!]"
        svg = images.inline_text_image(text, resp, styles=self.styles())
        
        return resp


class SendEmailView(View):

    def post(self, request):
        to_email = request.POST['email']
        # footer_resp = FooterRequest.as_view()(request)
	# footer_resp.render()
        request_id = random_num() #@TODO

        body_tmpl = Template("""
        Hello! Your footer is below: <br><br>

        -Footer <br><br>
        
        ====== <br<br>
        
        {% autoescape off %}
        {{ footer }}
        {% endautoescape %}
        """)

        view_instance = FooterEmailInstance()
        view_instance.request = request
        # @TODO render HTML from this view instance

        body = body_tmpl.render(Context({
            'footer': render_to_string(
                'email.html', 
                request=request,
                context={'view': {
                    'styles': view_instance.styles(),
                    'ga_image_url': view_instance.ga_image_url() 
                }})
            }))

        subject = 'Footer project test #{}'.format(request_id)
        body = body.encode('utf8')
        from_email = 'footer@bunsen.town'

        if settings.DEBUG:
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
