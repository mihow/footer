from django import template
from django.utils.safestring import mark_safe
#from django.template.defaultfilters import stringfilter

register = template.Library()


@register.simple_tag(takes_context=True, name='ii')
def inline_image(context, text):
    uuid = context.get('uuid', 'id')
    #text = "%s-%s" % (text, uuid)
    src = '/text.png?text=%s&id=%s' % (text, uuid)
    tag = '<img src="%s" alt="%s" title="%s">' % (src, text, text)
    return mark_safe(tag)
