from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField



class Footer(models.Model):
    uuid = models.IntegerField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class FooterRequest(models.Model):
    footer = models.ForeignKey(Footer, null=True, blank=True)
    request_data = JSONField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class FooterImage(models.Model):
    footer = models.ForeignKey(Footer, null=True, blank=True)
    request = models.ForeignKey(FooterRequest, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
