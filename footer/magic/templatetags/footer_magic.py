from django import template
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
#from django.template.defaultfilters import stringfilter

register = template.Library()


@register.simple_tag(takes_context=True, name='ii')
def inline_image(context, param):
    request = context['request']
    src = request.build_absolute_uri(reverse('inline_text_image', args=[param]))
    tag = '<img src="%s" alt="%s" style="vertical-align: sub;">' % (src, param)
    return mark_safe(tag)

@register.simple_tag(takes_context=True, name='ia')
def inline_animation(context, param):
    request = context['request']
    src = request.build_absolute_uri(reverse('inline_text_animation', args=[param]))
    tag = '<img src="%s" alt="%s" style="vertical-align: sub;">' % (src, param)
    return mark_safe(tag)

@register.simple_tag(takes_context=True, name='leader')
def leader_image(context, position):
    request = context['request']
    position = position or 'orphan'
    src = request.build_absolute_uri(reverse('leader_image'))
    tag = '<img src="%s?%s" alt="%s" style="vertical-align: sub;">' % (src, position, position)
    return mark_safe(tag)
