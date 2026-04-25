# ============================================================
# apps/modules/templatetags/module_tags.py
# Custom template tags for module tab rendering
# ============================================================
from django import template
from django.template.loader import render_to_string
from django.template.exceptions import TemplateDoesNotExist

register = template.Library()


@register.simple_tag(takes_context=True)
def include_tab3(context, module):
    """
    Render module-specific TAB3 template with fallback to M1 default.
    Usage: {% include_tab3 module %}
    """
    specific = f'modules/tabs/tab3_activity_{module.code.lower()}.html'
    fallback = 'modules/tabs/tab3_activity.html'
    ctx = dict(context.flatten())
    for template_name in [specific, fallback]:
        try:
            return render_to_string(template_name, ctx, request=context.get('request'))
        except TemplateDoesNotExist:
            continue
    return ''


@register.simple_tag(takes_context=True)
def include_tab4(context, module, content_html=''):
    """
    Render module-specific TAB4 template with fallback to generic.
    Usage: {% include_tab4 module content_html %}
    """
    specific = f'modules/tabs/tab4_assessment_{module.code.lower()}.html'
    fallback = 'modules/tabs/tab4_assessment_generic.html'
    ctx = dict(context.flatten())
    ctx['content_html'] = content_html  # explicit override
    for template_name in [specific, fallback]:
        try:
            return render_to_string(template_name, ctx, request=context.get('request'))
        except TemplateDoesNotExist:
            continue
    return ''


@register.simple_tag(takes_context=True)
def include_tab5(context, module, **kwargs):
    """
    Render module-specific TAB5 template with fallback to default.
    Usage: {% include_tab5 module saved_tensions=saved_tensions %}
    """
    specific = f'modules/tabs/tab5_reflection_{module.code.lower()}.html'
    fallback = 'modules/tabs/tab5_reflection.html'
    ctx = dict(context.flatten())
    ctx.update(kwargs)
    for template_name in [specific, fallback]:
        try:
            return render_to_string(template_name, ctx, request=context.get('request'))
        except TemplateDoesNotExist:
            continue
    return ''