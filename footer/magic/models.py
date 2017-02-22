from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField



class Footer(models.Model):
# class FooterInstance(models.Model):
    uuid = models.IntegerField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return "Footer #%s" % self.uuid

    def locations(self):
        requests = self.footer_requests.all().order_by('-created')
        locations = [r.request_data.get('location') for r in requests if r.request_data]
        return locations

    def dates_requested(self):
        requests = self.footer_requests.all().only('created').order_by('-created')
        dates = [r.created for r in requests]
        return sorted(dates)

    def num_requests(self):
        return self.footer_requests.count()

    class Meta:
        ordering = ['-created']


class FooterRequest(models.Model):
    footer = models.ForeignKey(Footer, null=True, blank=True)
    request_data = JSONField(null=True, blank=True, editable=False)
    is_leader = models.BooleanField(default=False, editable=False)
    image = models.ImageField(null=True, blank=True, editable=False)

    location = JSONField(null=True, blank=True, editable=False)
    user_agent = models.CharField(max_length=1024, null=True, blank=True, editable=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True, editable=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def footer_name(self):
        if self.footer:
            return "Footer #%s" % self.footer.uuid
        else:
            return "Footer ?"

    def __str__(self):
        return "Request #%s for %s%s" % (
            self.id, 
            self.footer_name(),
            " - LEADER" if self.is_leader else "",)

    def location_str(self):
        if self.location:
            if hasattr(self.location, 'items'):
                city = str(self.location.get('city'))
                country = str(self.location.get('country'))
                return ", ".join([c for c in [city, country] if c])
        return "Unknown"


    def lookup(self, key):
        """
        Fetch a variable from the request data JSON
        which can look very different depending on the
        original HTTP request.
        """
        key = str(key)
        if self.request_data:
            if key in self.request_data:
                return self.request_data[key]
            elif key.lower() in self.request_data: 
                return self.request_data[key.lower()]
            else:
                return None
        else:
            return None

    def is_leader_start(self):
        if 'start' in self.lookup('QUERY_STRING'):
            return True
        else:
            return False
    is_leader_start.boolean = True

    def is_leader_end(self):
        if 'end' in self.lookup('QUERY_STRING'):
            return True
        else:
            return False
    is_leader_end.boolean = True

    # def user_agent(self):
    #     return self.lookup('HTTP_USER_AGENT') or self.lookup('USER_AGENT')

    class Meta:
        ordering = ['-created']
