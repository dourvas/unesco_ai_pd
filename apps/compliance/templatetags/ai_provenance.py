"""
Phase C C.3 commit 3 — template tags for AI provenance disclosure.

Two tags:

  - `{% ai_provenance for=record %}` — emits one row in an XAI panel's
    `grid grid-cols-[auto_1fr]` surfacing the per-artefact timestamp.
    Inclusion tag rendering a tiny partial. Renders nothing if `for`
    is falsy (e.g., the artefact has no provenance row yet).

  - `{% ai_provenance_jsonld provenances %}` — emits a single
    `<script type="application/ld+json">` block on a page, declaring
    every AI-generated artefact on the page as schema.org/CreativeWork
    nodes with a SoftwareApplication creator. The view passes a list
    of `AIArtefactProvenance` rows; the tag handles serialisation +
    `escapejs`-safe inclusion.

Article 50(2) of the EU AI Act recommends machine-readable provenance
for synthetic content. The first tag handles the per-element label;
the second handles the page-level structured-data block. Both pull
from the same `AIArtefactProvenance` rows so the surface remains
internally consistent.
"""

import json

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.inclusion_tag('compliance/_ai_provenance_row.html')
def ai_provenance(for_=None, **kwargs):
    """Emit a `Generated at: <timestamp>` row inside an XAI panel's grid.

    Usage in template::

        {% ai_provenance for=progress.rag_feedback_provenance %}

    The `for_` parameter is unusual: Django templatetags do not allow
    `for` as a positional keyword (it conflicts with the `{% for %}`
    block tag at the lexer level). Callers should use `for=value` which
    routes through **kwargs to the `for_` parameter declared here.

    Renders nothing if `for_` is falsy (no provenance row attached to
    the artefact yet — legacy artefacts pre-backfill, or future kinds).
    """
    provenance = for_ or kwargs.get('for', None)
    return {'provenance': provenance}


@register.simple_tag
def ai_provenance_jsonld(provenances):
    """Emit a page-level `<script type="application/ld+json">` block.

    `provenances` is an iterable of `AIArtefactProvenance` rows.
    Each row becomes one schema.org/CreativeWork node:

        {
          "@type": "CreativeWork",
          "identifier": "<kind>#<pk>",
          "dateCreated": "<iso>",
          "creator": {"@type": "SoftwareApplication", "name": "<model>"},
          "isAccessibleForFree": true,
          "about": "AI-generated artefact (PROODOS)"
        }

    The tag returns an empty string if `provenances` is falsy — pages
    with no AI artefacts simply omit the script tag.

    Output is wrapped in `mark_safe` because we control the entire
    string construction; `json.dumps` is XSS-safe for our value set
    (no user-controlled fields).
    """
    rows = list(provenances or [])
    if not rows:
        return ''

    graph = []
    for prov in rows:
        graph.append({
            '@type': 'CreativeWork',
            'identifier': f'{prov.artefact_kind}#{prov.artefact_pk}',
            'dateCreated': prov.generated_at.isoformat() if prov.generated_at else None,
            'creator': {
                '@type': 'SoftwareApplication',
                'name': prov.model_name,
            },
            'isAccessibleForFree': True,
            'about': f'AI-generated {prov.artefact_kind.replace("_", " ")} (PROODOS)',
        })

    payload = {
        '@context': 'https://schema.org',
        '@graph': graph,
    }
    # `json.dumps(default=str)` would coerce datetimes, but we already
    # normalised to ISO strings above; pass ensure_ascii=False to keep
    # any Unicode in `about` strings intact.
    serialised = json.dumps(payload, ensure_ascii=False)
    return mark_safe(
        f'<script type="application/ld+json">{serialised}</script>'
    )
