from django import template
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
#from django.template.defaultfilters import stringfilter

register = template.Library()


@register.simple_tag(takes_context=True, name='ii')
def inline_image(context, text):
    uuid = context.get('uuid', 'id')
    request = context['request']
    #text = "%s-%s" % (text, uuid)
    src = request.build_absolute_uri(reverse('inline_text_image'))
    src = '%s?text=%s&id=%s' % (src, text, uuid)
    tag = '<img src="%s" alt="%s" title="%s">' % (src, text, text)
    return mark_safe(tag)
