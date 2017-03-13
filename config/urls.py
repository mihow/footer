# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.views import defaults as default_views
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt # @TODO needed?

from footer.magic.views import (
        TestImageView, 
        InlineTextImage, 
        InlineTextAnimation, 
        LeaderImageView, 
        IndexView, 
        SendEmailView,
        FooterEmailInstance,
        MapLink)

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/email_preview'), name='home'),
    url(r'^demo/?$', IndexView.as_view(), name='demo'),

    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('footer.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    url(r'^redirect.png', RedirectView.as_view(url='/image.png'), name='image_redirect'),
    #url(r'^image(?P<uuid>\w+)?.jpg$', FooterView.as_view(), name='test_image'),
    url(r'^image.png', never_cache(TestImageView.as_view()), name='test_image'),
    #url(r'^text.png', never_cache(InlineTextImage.as_view()), name='inline_text_image'),
    url(r'^text/(?P<param>\w+)?.png$', 
        never_cache(InlineTextImage.as_view()), name='inline_text_image'),
    url(r'^animation/(?P<param>\w+)?.gif$', 
        never_cache(InlineTextAnimation.as_view()), name='inline_text_animation'),

    url(r'^leader.gif', never_cache(LeaderImageView.as_view()), name='leader_image'),

    url(r'^email_preview/?$', FooterEmailInstance.as_view(),
        name='email_preview'),

    url(r'^send_email/?$', csrf_exempt(SendEmailView.as_view()), name='send_email'),
    url(r'^map', MapLink.as_view(), name='map'), 


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
