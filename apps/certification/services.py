"""
Services for apps.certification — Phase H.3 part 2.

Eligibility, issuance, and PDF rendering for the Certificate of
Attendance. The teacher-facing download view is a thin wrapper around
`get_or_issue_certificate(user)` + `render_certificate_pdf(certificate)`.

Design proposal:
  proodos_files/PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md
  §5 (Certificate of Attendance).

Article 50(2) machinery preserved from the dormant
`apps/epilogue/views.py::_generate_portrait_pdf` helper (Phase G
closure §3.3): JSON-LD body block + PDF document metadata via
`<meta>` tags read by xhtml2pdf. The certificate is NOT an AI
artefact (no LLM call generates any part of it); the JSON-LD body
therefore asserts `aiInvolved: false` with a `programmeUsesAI: true`
companion key pointing to the AI Impact Assessment URL.
"""

import io
import os

from django.conf import settings

from apps.certification.models import (
    CertificateOfAttendance,
    generate_verification_code,
)


# ----------------------------------------------------------------------
# Font registration for the bilingual certificate PDF
# ----------------------------------------------------------------------
# xhtml2pdf's default Helvetica/Times built-in fonts do not carry Greek
# glyphs with tones — they render as black-square placeholders. We
# register Noto Sans + Noto Serif from static/fonts/proodos_pdf/ which
# carry full Greek coverage (Google Noto fonts are designed for
# universal Unicode reach). Registration happens once at module import;
# reportlab's pdfmetrics is idempotent on duplicate registrations.

_FONTS_REGISTERED = False


def _register_certificate_fonts():
    """Register sans + serif fonts with full Greek coverage.

    Safe to call repeatedly — module-level flag guards re-registration.
    Resolution order per logical family:
      1. Bundled static/fonts/proodos_pdf/ — drop-in slot for a future
         open-licensed font with full Greek (e.g. real Google Noto
         Sans/Serif Greek). Files must contain Greek glyphs to be
         useful — the Windows-bundled Noto variants are Latin-only
         subsets and will fail to render Greek tones correctly.
      2. Windows system fonts (C:/Windows/Fonts/arial.ttf, times.ttf)
         — Arial and Times New Roman both carry full Greek including
         tonal diacritics; this is the working fallback on the dev
         machine and any Windows pilot host.
      3. Linux fallbacks left as TODO for the day the platform deploys
         off Windows.

    Logical family names used by the template CSS are "PdfSans" and
    "PdfSerif" — the template stays font-agnostic; this helper picks
    the best available file for each.
    """
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    from reportlab.pdfbase.ttfonts import TTFont

    bundled_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'proodos_pdf')
    windows_dir = 'C:/Windows/Fonts'

    families = [
        # (logical_family, [(regular_candidates), (bold_candidates)])
        (
            'PdfSans',
            [
                # Future drop-in: full-Greek Noto Sans, if bundled.
                os.path.join(bundled_dir, 'NotoSansGreek-Regular.ttf'),
                # Windows fallback: Arial carries full Greek.
                os.path.join(windows_dir, 'arial.ttf'),
            ],
            [
                os.path.join(bundled_dir, 'NotoSansGreek-Bold.ttf'),
                os.path.join(windows_dir, 'arialbd.ttf'),
            ],
        ),
        (
            'PdfSerif',
            [
                os.path.join(bundled_dir, 'NotoSerifGreek-Regular.ttf'),
                # Windows fallback: Times New Roman carries full Greek.
                os.path.join(windows_dir, 'times.ttf'),
            ],
            [
                os.path.join(bundled_dir, 'NotoSerifGreek-Bold.ttf'),
                os.path.join(windows_dir, 'timesbd.ttf'),
            ],
        ),
    ]

    def _first_existing(candidates):
        for path in candidates:
            if os.path.exists(path):
                return path
        raise RuntimeError(
            f'No usable font found among candidates: {candidates}. '
            f'Install Arial/Times on Windows or drop a Greek-capable '
            f'font into static/fonts/proodos_pdf/.'
        )

    for family, regular_candidates, bold_candidates in families:
        regular_path = _first_existing(regular_candidates)
        bold_path = _first_existing(bold_candidates)
        pdfmetrics.registerFont(TTFont(family, regular_path))
        pdfmetrics.registerFont(TTFont(f'{family}-Bold', bold_path))
        # Register the family so xhtml2pdf can resolve `font-weight: bold`
        # via the bold variant.
        registerFontFamily(family, normal=family, bold=f'{family}-Bold')

    _FONTS_REGISTERED = True


# ----------------------------------------------------------------------
# Eligibility
# ----------------------------------------------------------------------

def teacher_is_eligible(user) -> bool:
    """Has the user completed the closing AILST administration (T2)?

    Uses `completed_at__isnull=False` rather than a generic submission
    timestamp: per AilstResponse model docstring
    (apps/ailst/models.py:113-115), `completed_at` is set only when
    `responses` has all 36 paper_code keys and the derived scores are
    filled. So this gate already guarantees a complete T2, not a
    partial submission. No `is_complete` flag needed.
    """
    from apps.ailst.models import AilstResponse

    return AilstResponse.objects.filter(
        user=user,
        timepoint='T2',
        completed_at__isnull=False,
    ).exists()


# ----------------------------------------------------------------------
# Frozen-state builders
# ----------------------------------------------------------------------

def build_modules_summary() -> list:
    """Snapshot the 15-module catalogue at issuance time.

    Returned shape (frozen onto CertificateOfAttendance.modules_summary):

        [
            {"code": "M1", "title": "...",
             "aspect": "Human-Centred Mindset", "level": "Acquire"},
            ...
        ]

    Uses the human-readable display values for aspect + level (not the
    raw enum keys) so the PDF template renders them directly without
    needing to map. Order: by Module.order_index.
    """
    from apps.modules.models import Module

    rows = []
    for module in Module.objects.order_by('order_index'):
        rows.append({
            'code': module.code,
            'title': module.title,
            'aspect': module.get_unesco_aspect_display(),
            'level': module.get_proficiency_level_display(),
        })
    return rows


def _build_teacher_display(user) -> str:
    """Standard cascade for the human-readable teacher name."""
    return user.get_full_name() or user.username or 'PROODOS teacher'


def _instrument_version_for_t2(user) -> str:
    """The AILST instrument_version of the user's T2 row.

    Used to pin which AILST validation envelope the certificate was
    issued against (typically 'ning_2025_v1'). If multiple T2 rows
    exist (defensive — there should be at most one per AilstResponse
    Meta constraint), takes the most-recently completed.
    """
    from apps.ailst.models import AilstResponse

    row = (
        AilstResponse.objects
        .filter(user=user, timepoint='T2', completed_at__isnull=False)
        .order_by('-completed_at')
        .first()
    )
    if row is None:
        # Caller should have already gated on teacher_is_eligible(); this
        # is a defensive default that lets the certificate still issue
        # rather than crashing on an inconsistent state.
        return 'unknown'
    return row.instrument_version


# ----------------------------------------------------------------------
# Issuance
# ----------------------------------------------------------------------

def get_or_issue_certificate(user) -> CertificateOfAttendance:
    """Idempotent: returns the existing certificate or issues a new one.

    Frozen snapshot at issue time: teacher_display + modules_summary +
    instrument_version_t2. Later profile renames or M15 content edits
    do not alter the issued certificate (matches the
    EpilogueCompletion.stage0_snapshot first-entry-freeze pattern).

    Raises RuntimeError if the user is not yet eligible — the
    download view gates on `teacher_is_eligible(user)` before calling
    this helper, so a RuntimeError here indicates a programming bug
    (gate bypassed) rather than a user-facing error.
    """
    existing = CertificateOfAttendance.objects.filter(user=user).first()
    if existing is not None:
        return existing

    if not teacher_is_eligible(user):
        raise RuntimeError(
            'get_or_issue_certificate called for an ineligible user; '
            'call site must gate on teacher_is_eligible() first.'
        )

    return CertificateOfAttendance.objects.create(
        user=user,
        verification_code=generate_verification_code(),
        teacher_display=_build_teacher_display(user),
        modules_summary=build_modules_summary(),
        instrument_version_t2=_instrument_version_for_t2(user),
    )


# ----------------------------------------------------------------------
# PDF rendering
# ----------------------------------------------------------------------

def render_certificate_pdf(certificate, language=None) -> tuple:
    """Render the certificate as a PDF via reportlab Platypus.

    Returns `(pdf_bytes, filename)`. Raises RuntimeError on
    construction errors so the caller (download view) can decide
    between failing the request and re-rendering on demand.

    Mono-language: the certificate ships in exactly one language per
    deploy. The choice is fixed by `settings.CERTIFICATE_LANGUAGE`
    (default 'en'); the planned Greek branch overrides to 'el'. No
    per-user detection, no in-PDF toggle. Caller may pass `language=`
    explicitly to override the setting (used by tests to exercise
    both branches without forking settings).

    History notes for the next archaeologist:
      - Originally an xhtml2pdf wrapper rendering an HTML template,
        replaced by direct Platypus construction after xhtml2pdf
        rendered Greek-with-tones as black squares regardless of
        font (verified with bundled Noto + system Arial + system
        Times, all carrying full Greek glyphs). reportlab via
        Platypus handles the same Unicode without issue.
      - Originally bilingual EN+EL in one PDF per Phase H Path A
        (proposal §5.5), replaced 2026-05-26 by mono-language
        per-branch after PI feedback: "οι Έλληνες να παίρνουν
        ελληνικό πιστοποιητικό, οι υπόλοιποι αγγλικό". A planned
        Greek Git branch will flip the setting.

    Article 50(2) PDF document metadata (Title / Author / Subject /
    Creator / Keywords) is set on the SimpleDocTemplate constructor;
    reportlab writes these into the PDF Info dict. The JSON-LD
    "aiInvolved=false / programmeUsesAI=true" assertion is rendered
    as a small final paragraph so it embeds in the PDF text layer
    (greppable by automated EU AI Act conformance tools).
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Spacer

    # Register PdfSans + PdfSerif with reportlab. Safe to call
    # repeatedly (module-level guard).
    _register_certificate_fonts()

    if language is None:
        language = settings.CERTIFICATE_LANGUAGE
    if language not in ('en', 'el'):
        raise ValueError(
            f'Unsupported certificate language: {language!r}. '
            f"Supported: 'en', 'el'."
        )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        # Compressed margins (single-page target): 1.4cm sides /
        # 1.3cm top / 1.5cm bottom. Earlier values (1.8/2.0/2.2)
        # pushed content onto a second page once the Greek
        # standfirst + body + Όροι footer all sat on the same
        # canvas.
        leftMargin=1.4 * cm,
        rightMargin=1.4 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.5 * cm,
        # Article 50(2) PDF Info dict metadata — written into the
        # PDF metadata layer by reportlab.
        title=f'PROODOS Certificate of Attendance — {certificate.teacher_display}',
        author='International Hellenic University (IHU) — PROODOS Doctoral Research',
        subject='Certificate of Attendance — 15-module PROODOS programme',
        creator='PROODOS EduAI platform — apps/certification',
        keywords='PROODOS, certificate of attendance, UNESCO AI CFT, IHU, teacher professional development',
    )

    styles = _certificate_paragraph_styles()
    body_block = (
        _certificate_english_block if language == 'en'
        else _certificate_greek_block
    )

    story = []
    story.extend(body_block(certificate, styles))
    story.append(Spacer(1, 0.5 * cm))
    story.extend(_certificate_footer_block(certificate, styles, language))

    try:
        doc.build(story)
    except Exception as exc:
        raise RuntimeError(
            f'reportlab failed to build certificate {certificate.pk}: {exc}'
        ) from exc

    filename = (
        f'PROODOS_Certificate_of_Attendance_{language}_'
        f'{certificate.verification_code}.pdf'
    )
    return buf.getvalue(), filename


# ----------------------------------------------------------------------
# Platypus building blocks for the certificate
# ----------------------------------------------------------------------

def _certificate_paragraph_styles():
    """Return a dict of named ParagraphStyles used by the certificate.

    Centralised so the EN block + EL block + footer share consistent
    visual register (eyebrow + serif numeral + standfirst + body).
    """
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.styles import ParagraphStyle

    color_eyebrow = colors.HexColor('#6b7280')
    color_body = colors.HexColor('#1f2937')
    color_muted = colors.HexColor('#4b5563')
    color_holder = colors.HexColor('#111827')

    # Compressed sizes for single-page A4 target. Each style trims
    # leading + spaceAfter where readable without crowding.
    return {
        'eyebrow': ParagraphStyle(
            'eyebrow', fontName='PdfSans', fontSize=7.5,
            textColor=color_eyebrow, leading=10, spaceAfter=2,
        ),
        'numeral': ParagraphStyle(
            'numeral', fontName='PdfSerif-Bold', fontSize=24,
            textColor=color_body, leading=28, spaceAfter=4,
        ),
        'standfirst': ParagraphStyle(
            'standfirst', fontName='PdfSans', fontSize=10,
            textColor=colors.HexColor('#374151'), leading=13,
            spaceAfter=8,
        ),
        'holder': ParagraphStyle(
            'holder', fontName='PdfSerif-Bold', fontSize=16,
            textColor=color_holder, leading=19, spaceAfter=2,
        ),
        'meta_row': ParagraphStyle(
            'meta_row', fontName='PdfSans', fontSize=8.5,
            textColor=color_muted, leading=11, spaceAfter=3,
        ),
        'body': ParagraphStyle(
            'body', fontName='PdfSans', fontSize=9,
            textColor=color_body, leading=12, spaceAfter=4,
        ),
        'ornament': ParagraphStyle(
            'ornament', fontName='PdfSans', fontSize=10,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER, leading=12, spaceBefore=4,
            spaceAfter=4,
        ),
        'footer_heading': ParagraphStyle(
            'footer_heading', fontName='PdfSans-Bold', fontSize=7.5,
            textColor=color_body, leading=10, spaceBefore=4,
            spaceAfter=1,
        ),
        'footer': ParagraphStyle(
            'footer', fontName='PdfSans', fontSize=6.5,
            textColor=color_eyebrow, leading=9, spaceAfter=2,
        ),
        'footer_italic': ParagraphStyle(
            'footer_italic', fontName='PdfSans', fontSize=6.5,
            textColor=color_muted, leading=9, spaceAfter=2,
        ),
        'jsonld': ParagraphStyle(
            'jsonld', fontName='Courier', fontSize=5,
            textColor=colors.HexColor('#9ca3af'), leading=6,
            spaceBefore=3,
        ),
    }


def _certificate_modules_table(modules, header_labels, language='en'):
    """Return a Platypus Table flowable rendering the 15-module list.

    `modules` is the frozen modules_summary JSON from the certificate
    (English aspect/level labels since the model stores
    `get_*_display()` values at issue time). `header_labels` is a
    4-tuple of column-header strings passed in by the caller so EN
    and EL blocks render the same data with localised column titles.

    When `language='el'`, the per-cell aspect + level values are
    translated to Greek via a fixed mapping. Module codes + titles
    pass through unchanged (titles are content-language, set in the
    Module model and out of scope for this helper).
    """
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import Table, TableStyle

    # Greek translation map for the enum-derived English display
    # labels. Synchronised with Module.unesco_aspect / proficiency_level
    # choices in apps/modules/models.py — update both sides if the
    # source labels ever change.
    aspect_el = {
        'Human-Centred Mindset': 'Ανθρωποκεντρική Σκέψη',
        'Ethics': 'Δεοντολογία',
        'AI Foundations': 'Βάσεις ΤΝ',
        'AI Pedagogy': 'Παιδαγωγική της ΤΝ',
        'Professional Development': 'Επαγγελματική Ανάπτυξη',
    }
    level_el = {
        'Acquire': 'Βασικό Επίπεδο',
        'Deepen': 'Εμβάθυνση',
        'Create': 'Δημιουργία',
    }

    data = [list(header_labels)]
    for m in modules:
        aspect = m['aspect']
        level = m['level']
        if language == 'el':
            aspect = aspect_el.get(aspect, aspect)
            level = level_el.get(level, level)
        data.append([m['code'], m['title'], aspect, level])

    tbl = Table(
        data,
        # Compressed widths to fit within compressed margins
        # (page width ~18.2cm after 1.4cm margins).
        colWidths=[1.6 * cm, 8.0 * cm, 5.6 * cm, 3.0 * cm],
        repeatRows=1,
    )
    tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'PdfSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 6.5),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#6b7280')),
        ('FONTNAME', (0, 1), (-1, -1), 'PdfSans'),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1f2937')),
        ('LINEBELOW', (0, 0), (-1, -1), 0.4, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
    ]))
    return tbl


def _certificate_english_block(certificate, styles):
    """English certificate body flowables (full, not parallel)."""
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.units import cm

    issued_str = certificate.issued_at.strftime('%d %B %Y')
    code = certificate.verification_code
    weeks = settings.CERTIFICATE_PROGRAMME_WEEKS
    hours = settings.CERTIFICATE_PROGRAMME_HOURS

    return [
        Paragraph(
            'INTERNATIONAL HELLENIC UNIVERSITY &nbsp;·&nbsp; PROODOS DOCTORAL RESEARCH',
            styles['eyebrow'],
        ),
        Paragraph('Certificate of Attendance', styles['numeral']),
        Paragraph(
            'This certificate attests to the completion of the 15-module '
            'PROODOS professional-development programme on AI literacy for '
            'K-12 educators, aligned to the UNESCO AI Competency Framework '
            'for Teachers (UNESCO ICT-CFT).',
            styles['standfirst'],
        ),
        Paragraph(certificate.teacher_display, styles['holder']),
        Paragraph(
            f'Issued on {issued_str} &nbsp;·&nbsp; Verification code: '
            f'<font face="Courier" color="#111827">{code}</font>',
            styles['meta_row'],
        ),
        Paragraph(
            f'Programme duration: <b>{weeks} weeks</b> &nbsp;·&nbsp; '
            f'Total study hours: <b>{hours} hours</b>',
            styles['meta_row'],
        ),
        Paragraph('• • •', styles['ornament']),
        Paragraph(
            'The holder has completed all 15 modules of the PROODOS '
            'programme, structured around five UNESCO competency aspects '
            '(Human-Centred Mindset, Ethics, AI Foundations, AI Pedagogy, '
            'Professional Development) at three proficiency levels '
            '(Acquire, Deepen, Create). The 15 modules completed are '
            'listed below.',
            styles['body'],
        ),
        Spacer(1, 0.3 * cm),
        _certificate_modules_table(
            certificate.modules_summary,
            header_labels=('Module', 'Title', 'UNESCO Aspect', 'Level'),
            language='en',
        ),
    ]


def _certificate_greek_block(certificate, styles):
    """Greek certificate body flowables (full, not parallel).

    Production-ready as of 2026-05-26 — DRAFT watermark dropped when
    the mono-language per-branch model replaced bilingual. Text wording
    revised 2026-05-26 from the PI's improved Greek draft (more formal
    register; explicit labels for holder name + issuance date +
    verification code + duration; "Βασικό Επίπεδο" replaces "Πρόσκτηση"
    in the level vocabulary, propagated also to the table translation
    map in `_certificate_modules_table`).
    """
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.units import cm

    issued_str_el = certificate.issued_at.strftime('%d/%m/%Y')
    code = certificate.verification_code
    weeks = settings.CERTIFICATE_PROGRAMME_WEEKS
    hours = settings.CERTIFICATE_PROGRAMME_HOURS

    return [
        Paragraph(
            'ΔΙΕΘΝΕΣ ΠΑΝΕΠΙΣΤΗΜΙΟ ΤΗΣ ΕΛΛΑΔΟΣ &nbsp;·&nbsp; ΔΙΔΑΚΤΟΡΙΚΗ ΕΡΕΥΝΑ PROODOS',
            styles['eyebrow'],
        ),
        Paragraph('Βεβαίωση Παρακολούθησης', styles['numeral']),
        Paragraph(
            'Η παρούσα βεβαίωση πιστοποιεί την επιτυχή ολοκλήρωση του '
            'προγράμματος επαγγελματικής ανάπτυξης PROODOS, το οποίο '
            'αποτελείται από 15 ενότητες. Το αντικείμενό του αφορά στην '
            'παιδαγωγική αξιοποίηση της Τεχνητής Νοημοσύνης από '
            'εκπαιδευτικούς Πρωτοβάθμιας και Δευτεροβάθμιας εκπαίδευσης, '
            'ενώ είναι πλήρως εναρμονισμένο με το Πλαίσιο Δεξιοτήτων ΤΝ '
            'της UNESCO για Εκπαιδευτικούς.',
            styles['standfirst'],
        ),
        Paragraph(
            f'<b>Ονοματεπώνυμο:</b> {certificate.teacher_display}',
            styles['holder'],
        ),
        Paragraph(
            f'<b>Ημερομηνία Έκδοσης:</b> {issued_str_el} &nbsp;·&nbsp; '
            f'<b>Κωδικός Επαλήθευσης:</b> '
            f'<font face="Courier" color="#111827">{code}</font>',
            styles['meta_row'],
        ),
        Paragraph(
            f'<b>Διάρκεια Προγράμματος:</b> {weeks} εβδομάδες &nbsp;·&nbsp; '
            f'<b>Συνολικές Ώρες Παρακολούθησης:</b> {hours} ώρες',
            styles['meta_row'],
        ),
        Paragraph('• • •', styles['ornament']),
        Paragraph(
            'Ο/Η κάτοχος ολοκλήρωσε επιτυχώς και τις 15 ενότητες του '
            'προγράμματος PROODOS, οι οποίες είναι δομημένες γύρω από '
            'τους πέντε άξονες του πλαισίου δεξιοτήτων της UNESCO '
            '(Ανθρωποκεντρική Σκέψη, Δεοντολογία, Βάσεις ΤΝ, Παιδαγωγική '
            'της ΤΝ, Επαγγελματική Ανάπτυξη) και κατανέμονται σε τρία '
            'επίπεδα επάρκειας (Βασικό Επίπεδο, Εμβάθυνση, Δημιουργία). '
            'Οι 15 ενότητες παρατίθενται αναλυτικά παρακάτω:',
            styles['body'],
        ),
        Spacer(1, 0.15 * cm),
        _certificate_modules_table(
            certificate.modules_summary,
            header_labels=('Ενότητα', 'Τίτλος', 'Άξονας UNESCO', 'Επίπεδο'),
            language='el',
        ),
    ]


def _certificate_footer_block(certificate, styles, language):
    """Verification + no-AI-provenance + JSON-LD footer flowables.

    Language-aware: footer copy mirrors the body block's language.
    Two named sections in formal academic style ("Verification" +
    "Issuance & Compliance" in English, "Έλεγχος Εγκυρότητας" +
    "Όροι Έκδοσης & Συμμόρφωσης" in Greek), each with a small
    bold heading. JSON-LD metadata stays English (machine-readable
    layer; no translation needed).
    """
    from reportlab.platypus import Paragraph

    if language == 'el':
        verify_heading = 'Έλεγχος Εγκυρότητας:'
        verify_text = (
            'Μπορείτε να επαληθεύσετε την εγκυρότητα της παρούσας '
            'βεβαίωσης στην επίσημη σελίδα ελέγχου της πλατφόρμας, '
            'εισάγοντας τον παραπάνω κωδικό. Κατά την επαλήθευση '
            'εμφανίζονται αποκλειστικά το όνομα του κατόχου, η '
            'ημερομηνία έκδοσης και η λίστα των 15 ενοτήτων, '
            'διασφαλίζοντας την προστασία των προσωπικών δεδομένων, '
            'χωρίς την αποκάλυψη βαθμολογιών ή άλλων επιμέρους '
            'αναλυτικών στοιχείων.'
        )
        compliance_heading = 'Όροι Έκδοσης &amp; Συμμόρφωσης:'
        no_ai_text = (
            '<i>Η παρούσα βεβαίωση εκδίδεται αυτοματοποιημένα με '
            'βάση την ολοκλήρωση του τελικού εργαλείου '
            'αυτοαξιολόγησης. Η διαδικασία αξιολόγησης, ο '
            'υπολογισμός της βαθμολογίας και η έκδοση της '
            'βεβαίωσης βασίζονται αποκλειστικά σε προκαθορισμένα '
            'κριτήρια, χωρίς τη χρήση συστημάτων Τεχνητής '
            'Νοημοσύνης για τη λήψη αποφάσεων. Τα παιδαγωγικά '
            'εργαλεία της πλατφόρμας ενσωματώνουν λειτουργίες ΤΝ '
            '(οι οποίες περιγράφονται αναλυτικά στο AI Impact '
            'Assessment, στη διεύθυνση '
            '/compliance/about/ai-act-compliance/), η χρήση των '
            'οποίων κατά τη διάρκεια του προγράμματος δεν '
            'επηρεάζει τη διαδικασία πιστοποίησης.</i>'
        )
        version_line = (
            f'<i>Έκδοση προτύπου PDF: {certificate.pdf_metadata_version}</i>'
        )
    else:
        verify_heading = 'Verification:'
        verify_text = (
            'You may verify this certificate at the platform&apos;s '
            'official verification endpoint by entering the code above. '
            'The endpoint discloses only the holder&apos;s name, the '
            'date of issuance, and the list of 15 modules — no scores '
            'or factor breakdowns — preserving the holder&apos;s '
            'personal-data minimisation guarantee.'
        )
        compliance_heading = 'Issuance &amp; Compliance:'
        no_ai_text = (
            '<i>This certificate is issued automatically on completion '
            'of the closing self-assessment instrument. Eligibility '
            'determination, score calculation, and certificate '
            'generation rely solely on pre-defined criteria, with no '
            'AI systems involved in the decisioning. The platform&apos;s '
            'pedagogical features include AI tools (described in detail '
            'in the AI Impact Assessment at '
            '/compliance/about/ai-act-compliance/), whose use during '
            'the programme does not affect the certification '
            'process.</i>'
        )
        version_line = (
            f'<i>PDF template version: {certificate.pdf_metadata_version}</i>'
        )

    # Article 50(2) JSON-LD machine-readable provenance, rendered as
    # a small monospace paragraph so it embeds in the PDF text layer
    # and is greppable by automated EU AI Act conformance tools. The
    # aiInvolved=false claim is the central provenance assertion;
    # programmeUsesAI=true acknowledges the upstream programme's AI
    # tooling and points to the AI Impact Assessment. Stays English
    # regardless of body language (machine-readable layer; no
    # translation needed).
    jsonld = (
        '{"@context":"https://schema.org",'
        '"@type":"EducationalCredential",'
        '"name":"PROODOS Certificate of Attendance",'
        '"credentialCategory":"certificate of attendance",'
        '"issuedBy":{"@type":"EducationalOrganization",'
        '"name":"International Hellenic University",'
        '"alternateName":"\\u0394\\u0399.\\u03a0\\u0391.\\u0395."},'
        f'"recipient":"{certificate.teacher_display}",'
        f'"dateIssued":"{certificate.issued_at.isoformat()}",'
        f'"identifier":"{certificate.verification_code}",'
        f'"language":"{language}",'
        '"aiInvolved":false,'
        '"programmeUsesAI":true,'
        '"programmeAIImpactAssessmentURL":"/compliance/about/ai-act-compliance/",'
        f'"instrumentVersionT2":"{certificate.instrument_version_t2}",'
        f'"pdfMetadataVersion":"{certificate.pdf_metadata_version}",'
        f'"programmeDurationWeeks":{settings.CERTIFICATE_PROGRAMME_WEEKS},'
        f'"programmeTotalHours":{settings.CERTIFICATE_PROGRAMME_HOURS}}}'
    )

    return [
        Paragraph(verify_heading, styles['footer_heading']),
        Paragraph(verify_text, styles['footer']),
        Paragraph(compliance_heading, styles['footer_heading']),
        Paragraph(no_ai_text, styles['footer_italic']),
        Paragraph(version_line, styles['footer_italic']),
        Paragraph(jsonld, styles['jsonld']),
    ]
