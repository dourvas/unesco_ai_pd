"""
Template tags for TAB1 magazine-style layout.

Provides:
  - module_aspect_colour: maps module code -> UNESCO aspect colour palette
  - module_icon_svg:      maps module code -> inline lucide SVG
  - module_number_padded: zero-padded 2-digit module number (e.g. "01", "15")

Aspect mapping is canonical per the design handoff and is intentionally
keyed by module code rather than the modules.unesco_aspect DB field, which
contains inconsistent values across rows.
"""
import json

from django.utils.safestring import mark_safe
from django import template

register = template.Library()


@register.filter
def unwrap_overview(value):
    """
    Some module_overview rows are stored as a JSON blob like
    {"overview": "..."} instead of plain text (data inconsistency).
    Return the inner overview text when that's the case; otherwise return
    the value unchanged.
    """
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if not stripped.startswith("{"):
        return value
    try:
        data = json.loads(stripped)
    except (ValueError, TypeError):
        return value
    if isinstance(data, dict) and isinstance(data.get("overview"), str):
        return data["overview"]
    return value


# UNESCO Aspect -> colour palette (50 / 600 / 800-900 stops).
# Each entry contains:
#   main: 600-stop, used for hero number and icon foreground
#   bg:   50-stop,  used for icon background, badge background, accent fills
#   text: 800/900-stop, used for badge text
#   name: human-readable aspect name (used in the badge)
ASPECT_COLOURS = {
    1: {
        "main": "#BA7517",
        "bg":   "#FAEEDA",
        "text": "#633806",
        "name": "Human-Centred Mindset",
    },
    2: {
        "main": "#0F6E56",
        "bg":   "#E1F5EE",
        "text": "#04342C",
        "name": "Ethics",
    },
    3: {
        "main": "#185FA5",
        "bg":   "#E6F1FB",
        "text": "#042C53",
        "name": "AI Foundations",
    },
    4: {
        "main": "#993556",
        "bg":   "#FBEAF0",
        "text": "#4B1528",
        "name": "AI Pedagogy",
    },
    5: {
        "main": "#639922",
        "bg":   "#EAF3DE",
        "text": "#173404",
        "name": "Professional Development",
    },
}


# Canonical module -> aspect mapping (per design handoff)
MODULE_TO_ASPECT = {
    "M1": 1, "M6": 1, "M11": 1,
    "M2": 2, "M7": 2, "M12": 2,
    "M3": 3, "M8": 3, "M13": 3,
    "M4": 4, "M9": 4, "M14": 4,
    "M5": 5, "M10": 5, "M15": 5,
}


# Lucide SVG paths (MIT licensed, https://lucide.dev).
# Each value is the inner markup of a 24x24 lucide icon.
# Wrapped at render-time with stroke="currentColor" stroke-width="2"
# so they inherit the surrounding text colour.
_LUCIDE_PATHS = {
    "network": (
        '<rect x="16" y="16" width="6" height="6" rx="1"/>'
        '<rect x="2" y="16" width="6" height="6" rx="1"/>'
        '<rect x="9" y="2" width="6" height="6" rx="1"/>'
        '<path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/>'
        '<path d="M12 12V8"/>'
    ),
    "scale": (
        '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>'
        '<path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>'
        '<path d="M7 21h10"/>'
        '<path d="M12 3v18"/>'
        '<path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>'
    ),
    "atom": (
        '<circle cx="12" cy="12" r="1"/>'
        '<path d="M20.2 20.2c2.04-2.03.02-7.36-4.5-11.9-4.54-4.52-9.87-6.54-11.9-4.5-2.04 2.03-.02 7.36 4.5 11.9 4.54 4.52 9.87 6.54 11.9 4.5Z"/>'
        '<path d="M15.7 15.7c4.52-4.54 6.54-9.87 4.5-11.9-2.03-2.04-7.36-.02-11.9 4.5-4.52 4.54-6.54 9.87-4.5 11.9 2.03 2.04 7.36.02 11.9-4.5Z"/>'
    ),
    "wrench": (
        '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'
    ),
    "message-circle": (
        '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>'
    ),
    "user-check": (
        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<polyline points="16 11 18 13 22 9"/>'
    ),
    "shield-check": (
        '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>'
        '<path d="m9 12 2 2 4-4"/>'
    ),
    "pen-tool": (
        '<path d="M15.707 21.293a1 1 0 0 1-1.414 0l-1.586-1.586a1 1 0 0 1 0-1.414l5.586-5.586a1 1 0 0 1 1.414 0l1.586 1.586a1 1 0 0 1 0 1.414z"/>'
        '<path d="m18 13-1.375-6.874a1 1 0 0 0-.746-.776L3.235 2.028a1 1 0 0 0-1.207 1.207L5.35 15.879a1 1 0 0 0 .776.746L13 18"/>'
        '<path d="m2.3 2.3 7.286 7.286"/>'
        '<circle cx="11" cy="11" r="2"/>'
    ),
    "file-pen": (
        '<path d="M12.5 22H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8.5L20 7.5V11"/>'
        '<polyline points="14 2 14 8 20 8"/>'
        '<path d="M13.378 15.626a1 1 0 1 0 3.004 3.004l5.01-5.012a2 2 0 1 0-2.99-2.99z"/>'
    ),
    "refresh-cw": (
        '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>'
        '<path d="M21 3v5h-5"/>'
        '<path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>'
        '<path d="M3 21v-5h5"/>'
    ),
    "compass": (
        '<polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>'
        '<circle cx="12" cy="12" r="10"/>'
    ),
    "file-check": (
        '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5z"/>'
        '<polyline points="14 2 14 8 20 8"/>'
        '<path d="m9 15 2 2 4-4"/>'
    ),
    "image": (
        '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
        '<circle cx="9" cy="9" r="2"/>'
        '<path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>'
    ),
    "gamepad-2": (
        '<line x1="6" x2="10" y1="11" y2="11"/>'
        '<line x1="8" x2="8" y1="9" y2="13"/>'
        '<line x1="15" x2="15.01" y1="12" y2="12"/>'
        '<line x1="18" x2="18.01" y1="10" y2="10"/>'
        '<path d="M17.32 5H6.68a4 4 0 0 0-3.978 3.59c-.006.052-.01.101-.017.152C2.604 9.416 2 14.456 2 16a3 3 0 0 0 3 3c1 0 1.5-.5 2-1l1.414-1.414A2 2 0 0 1 9.828 16h4.344a2 2 0 0 1 1.414.586L17 18c.5.5 1 1 2 1a3 3 0 0 0 3-3c0-1.545-.604-6.584-.685-7.258-.007-.05-.011-.1-.017-.151A4 4 0 0 0 17.32 5z"/>'
    ),
    "trending-up": (
        '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
        '<polyline points="16 7 22 7 22 13"/>'
    ),
}


MODULE_TO_ICON = {
    "M1":  "network",
    "M2":  "scale",
    "M3":  "atom",
    "M4":  "wrench",
    "M5":  "message-circle",
    "M6":  "user-check",
    "M7":  "shield-check",
    "M8":  "pen-tool",
    "M9":  "file-pen",
    "M10": "refresh-cw",
    "M11": "compass",
    "M12": "file-check",
    "M13": "image",
    "M14": "gamepad-2",
    "M15": "trending-up",
}


def _aspect_for(module):
    code = getattr(module, "code", None) or str(module)
    return MODULE_TO_ASPECT.get(code, 3)  # default to AI Foundations (blue) if unknown


@register.simple_tag
def module_aspect_colour(module):
    """Return the aspect colour palette dict for a module."""
    return ASPECT_COLOURS[_aspect_for(module)]


@register.simple_tag
def module_aspect_name(module):
    """Return the human-readable aspect name for a module."""
    return ASPECT_COLOURS[_aspect_for(module)]["name"]


@register.simple_tag
def module_icon_svg(module):
    """
    Return inline SVG markup for a module's lucide icon.

    The SVG uses currentColor so the surrounding text/colour rules apply.
    """
    code = getattr(module, "code", None) or str(module)
    icon_name = MODULE_TO_ICON.get(code, "compass")
    paths = _LUCIDE_PATHS[icon_name]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true">'
        f'{paths}'
        '</svg>'
    )
    return mark_safe(svg)


@register.simple_tag
def module_number_padded(module):
    """Return the module number as a 2-digit zero-padded string ("01"-"15")."""
    code = getattr(module, "code", None) or str(module)
    if code.startswith("M"):
        try:
            return f"{int(code[1:]):02d}"
        except ValueError:
            return code
    return code
