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

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def footer_name(self):
        if self.footer:
            return "Footer #%s" % self.footer.uuid
        else:
            return "Anonymous Footer"

    def __str__(self):
        return "%sRequest id %s for %s" % (
            "Leader " if self.is_leader else "",
            self.id, 
            self.footer_name())

    class Meta:
        ordering = ['-created']
