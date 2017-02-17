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
    request_data = JSONField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "Request id for Footer #%s" % self.id, self.footer.uuid

    class Meta:
        ordering = ['-created']
