"""
Template filter for rendering plain-text consent copy as readable HTML
without forcing line breaks at the source's wrap column.

Background
----------
The verbatim consent texts in apps.compliance.copy are stored as Python
triple-quoted strings, wrapped at ~80 columns for source readability.
The source file is the canonical form (it is also what ConsentRecord
snapshots for audit). Rendering it through Django's `linebreaksbr`
filter turned every \n into <br>, which made every consent paragraph
visually hard-wrapped at the source's 80-column boundary regardless of
the container width — leaving a large right-side gap on a normal
desktop card layout.

This filter renders the same text correctly:

  - Blank lines (double \n) become paragraph boundaries -> <p>...</p>.
  - Inside a paragraph, single \n becomes a space, so the browser
    re-wraps the text at the container width.
  - A run of lines starting with "- " or "  - " is detected as a
    bullet list and rendered as <ul><li>...</li></ul>. The bullet
    marker is stripped from the rendered item text.
  - Indented continuation lines under a bullet stay attached to that
    bullet (joined with a space).
  - All output is HTML-escaped, then marked safe.
"""

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe


register = template.Library()


def _is_bullet(line):
    stripped = line.lstrip()
    return stripped.startswith('- ') or stripped == '-'


def _strip_bullet(line):
    stripped = line.lstrip()
    if stripped.startswith('- '):
        return stripped[2:].strip()
    if stripped == '-':
        return ''
    return stripped


def _render_paragraph(block):
    """Render one paragraph block (a sequence of non-empty lines).

    Decides between a flowing <p> (no bullets) and a <p>...</p> +
    <ul>...</ul> combo (a lead-in line followed by bullets, or pure
    bullets).
    """
    lines = block.split('\n')
    bullet_starts = [i for i, line in enumerate(lines) if _is_bullet(line)]

    if not bullet_starts:
        text = ' '.join(line.strip() for line in lines if line.strip())
        return f'<p>{escape(text)}</p>'

    parts = []
    first_bullet = bullet_starts[0]

    if first_bullet > 0:
        # Lead-in text before the first bullet.
        lead = ' '.join(line.strip() for line in lines[:first_bullet] if line.strip())
        if lead:
            parts.append(f'<p>{escape(lead)}</p>')

    items = []
    current = []
    for line in lines[first_bullet:]:
        if _is_bullet(line):
            if current:
                items.append(' '.join(current).strip())
                current = []
            current.append(_strip_bullet(line))
        else:
            # Continuation of the previous bullet.
            stripped = line.strip()
            if stripped:
                current.append(stripped)
    if current:
        items.append(' '.join(current).strip())

    list_html = '<ul class="list-disc pl-6 space-y-1">' + ''.join(
        f'<li>{escape(item)}</li>' for item in items if item
    ) + '</ul>'
    parts.append(list_html)
    return ''.join(parts)


@register.filter(name='consent_format')
def consent_format(text):
    """Render plain-text consent copy as HTML paragraphs and bullet lists.

    Usage in template:

        {% load consent_format %}
        ...
        {{ research_text|consent_format }}
    """
    if not text:
        return ''

    # Normalise CRLF -> LF and split on blank lines (paragraph boundaries).
    text = str(text).replace('\r\n', '\n').replace('\r', '\n')
    blocks = [block for block in text.split('\n\n') if block.strip()]

    rendered = ''.join(_render_paragraph(block) for block in blocks)
    return mark_safe(rendered)
