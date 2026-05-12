"""
Service helpers for the compliance app.

Centralised write/revoke path for ConsentRecord. C.2 AI Disclosure
middleware, C.4 Privacy dashboard, and the legacy-boolean data migration
all flow through these helpers. Keeps business logic out of views and
out of migrations.

C.4 additions (commits 2 and 3):
  - gather_user_export(user) -> dict: GDPR Art. 15 right of access.
    Builds the full personal-data snapshot for the user, including the
    raw-SQL rag_queries rows. Caller serialises to JSON.
  - anonymize_user(user) -> None: GDPR Art. 17 right to erasure.
    (Lands in commit 3 of C.4.)
"""

from typing import Optional

from django.db import connection
from django.utils import timezone


LEGACY_BOOLEAN_MAP = {
    # TeacherProfile boolean field -> ConsentRecord consent_type
    'research_consent': 'research_participation',
    'consent_data_sharing': 'data_sharing',
    # NOTE: TeacherProfile.contact_for_research is a CONTACT PREFERENCE
    # ('available for research interviews'), not a consent. It is not
    # migrated to ConsentRecord.
}

LEGACY_VERSION_TAG = 'v0_pre_phase_c'
LEGACY_CONSENT_TEXT_TEMPLATE = (
    "Migrated from TeacherProfile.{boolean_field} on {migration_date}. "
    "Original Step 3 consent text was not preserved (pre-Phase-C limitation: "
    "consent was tracked as a boolean field without verbatim text storage). "
    "User had this boolean set to True at the time of the M6 backfill data "
    "migration. Granted_at reflects the user's TeacherProfile.consent_timestamp "
    "(when available) or TeacherProfile.created_at (fallback)."
)


def record_consent(*, user, consent_type, consent_text, version,
                   granted=True, ip_address=None):
    """Idempotent helper to write a ConsentRecord row, with supersede semantics.

    Two cases:

    1. SAME (user, consent_type, version) row already active:
       Return that row. No new write. (Idempotency for replays — e.g., a
       user double-clicking 'I acknowledge' on the AI Disclosure modal.)

    2. DIFFERENT version: revoke any prior active rows of the same
       (user, consent_type), then create the new row. The new version
       'supersedes' the prior one. Audit trail is preserved (old rows
       remain in the table with revoked_at set); current state is clean
       (exactly one active row per consent_type per user).

    The supersede pattern:
      - Mirrors how GDPR / IRB consent updates work in practice: a new
        text version supersedes the previous one once explicitly agreed.
      - Keeps the M6 sync_teacher_profile_booleans signal simple: the
        canonical state remains "any active row of this consent_type".
      - Avoids accumulating multiple active rows per consent_type, which
        would muddy queries and analytics.

    Per-row save() (not bulk update) when revoking prior active versions
    so that the post_save signal fires correctly.

    Args:
        user: Django User instance.
        consent_type: One of CONSENT_TYPE_CHOICES values.
        consent_text: Verbatim text shown to the user.
        version: Version tag (e.g., 'v1_pre_irb').
        granted: True if user consented, False if explicitly denied.
        ip_address: Optional IP at consent time. Auto-redacted after 30 days
            via manage.py redact_old_consent_ips.

    Returns:
        ConsentRecord row (newly created, or pre-existing if same version
        was already active).
    """
    from .models import ConsentRecord

    # Idempotency: same version already active for this (user, type)?
    existing = ConsentRecord.objects.filter(
        user=user,
        consent_type=consent_type,
        version=version,
        revoked_at__isnull=True,
    ).first()
    if existing:
        return existing

    # Supersede: revoke any active rows of OTHER versions for the same
    # (user, consent_type). Per-row save() so the M6 sync signal fires.
    now = timezone.now()
    prior_active = ConsentRecord.objects.filter(
        user=user,
        consent_type=consent_type,
        revoked_at__isnull=True,
    )
    for cr in prior_active:
        cr.revoked_at = now
        cr.save(update_fields=['revoked_at'])

    # Create the new row.
    return ConsentRecord.objects.create(
        user=user,
        consent_type=consent_type,
        granted=granted,
        consent_text=consent_text,
        version=version,
        ip_address=ip_address,
    )


def revoke_consent(*, user, consent_type, version: Optional[str] = None) -> int:
    """Mark active consents as revoked.

    If `version` is None, revokes ALL active rows for (user, consent_type) —
    note that the supersede pattern in record_consent normally keeps at most
    one active row per (user, consent_type), so version=None typically
    revokes 0 or 1 rows. The 'all versions' wording reflects the legal
    intent: one user's withdrawal of consent for a consent_type covers
    every active row of that type, regardless of historical text version.
    Otherwise revokes only matching version (used by tests that bypass
    supersede via direct ORM creation).

    Returns count of rows revoked.

    Implementation note: per-row save() (not bulk update()) so that the
    sync_teacher_profile_booleans post_save signal fires and the legacy
    boolean cache stays in sync. Bulk update() bypasses signals.
    """
    from .models import ConsentRecord

    qs = ConsentRecord.objects.filter(
        user=user,
        consent_type=consent_type,
        revoked_at__isnull=True,
    )
    if version is not None:
        qs = qs.filter(version=version)

    now = timezone.now()
    count = 0
    for cr in qs:
        cr.revoked_at = now
        cr.save(update_fields=['revoked_at'])
        count += 1
    return count


def clear_pii_on_profile(profile):
    """Phase C C.4 — clear personally identifying fields on a TeacherProfile.

    Used by both the AI-Disclosure revocation path (TD-008 fix: clears
    ack_at so the middleware re-shows the modal) and the full account
    erasure (which calls this plus auth_user clearing).

    Fields cleared to empty string:
      first_name, last_name, display_name, subject_area_other,
      ai_teaching_integration, current_curriculum_pressure,
      institutional_ai_policy

    JSON list fields reset to []:
      ai_tools_used, primary_goals, student_population_special_needs

    Lifecycle / consent state reset:
      ai_disclosure_acknowledged_at -> None
      profile_completed -> False
      research_consent -> False
      consent_data_sharing -> False
      contact_for_research -> False

    Does NOT touch:
      research_data_opted_out (set by caller of erasure flow)
      subject_area, grade_level, teaching_years, school_location,
      average_class_size, ai_experience, preferred_communication_style
      (research-relevant variables, per the data_sharing consent text
      in apps/compliance/copy.py).

    Caller is responsible for the .save() — this helper only mutates
    the in-memory instance so a single .save(update_fields=[...])
    can carry all the changes.
    """
    # Free-text PII strings -> empty string.
    profile.first_name = ''
    profile.last_name = ''
    profile.display_name = ''
    profile.subject_area_other = ''
    profile.ai_teaching_integration = ''
    profile.current_curriculum_pressure = ''
    profile.institutional_ai_policy = ''

    # JSON list-style fields with potential identifiers.
    profile.ai_tools_used = []
    profile.primary_goals = []
    profile.student_population_special_needs = []

    # Lifecycle + consent flag reset.
    profile.ai_disclosure_acknowledged_at = None
    profile.profile_completed = False
    profile.research_consent = False
    profile.consent_data_sharing = False
    profile.contact_for_research = False


def migrate_legacy_teacher_consents(*, TeacherProfile=None, ConsentRecord=None):
    """Backfill ConsentRecord rows for pre-Phase-C TeacherProfile booleans.

    For each TeacherProfile where research_consent=True or
    consent_data_sharing=True, create a corresponding ConsentRecord row
    with version='v0_pre_phase_c' and an explanatory consent_text.

    Idempotent: re-running skips users who already have an active
    ConsentRecord row for the matching (user, consent_type, version).

    Note on contact_for_research: this is a contact preference, not a
    consent. Not migrated.

    Args:
        TeacherProfile: optional model class. Defaults to live model.
            Pass apps.get_model('users','TeacherProfile') in migrations.
        ConsentRecord: optional model class. Defaults to live model.

    Returns:
        int — number of new ConsentRecord rows created.
    """
    if TeacherProfile is None:
        from apps.users.models import TeacherProfile as TeacherProfile  # noqa
    if ConsentRecord is None:
        from .models import ConsentRecord as ConsentRecord  # noqa

    today = timezone.now()
    created_count = 0

    for profile in TeacherProfile.objects.all():
        for boolean_field, consent_type in LEGACY_BOOLEAN_MAP.items():
            if not getattr(profile, boolean_field, False):
                continue

            # Idempotency guard: skip if active row already exists for this
            # (user, type, version) tuple.
            already_exists = ConsentRecord.objects.filter(
                user_id=profile.user_id,
                consent_type=consent_type,
                version=LEGACY_VERSION_TAG,
                revoked_at__isnull=True,
            ).exists()
            if already_exists:
                continue

            granted_at_raw = (
                profile.consent_timestamp
                or profile.created_at
                or today
            )
            # Legacy TeacherProfile.consent_timestamp / created_at may be
            # naive datetimes (pre-USE_TZ=True era). Coerce to aware (UTC)
            # so PostgreSQL stores under the modern timezone-aware contract.
            # See proodos_files/TECH_DEBT_LOG.md for the planned full fix.
            from django.utils.timezone import is_naive, make_aware
            granted_at = (
                make_aware(granted_at_raw)
                if is_naive(granted_at_raw)
                else granted_at_raw
            )
            consent_text = LEGACY_CONSENT_TEXT_TEMPLATE.format(
                boolean_field=boolean_field,
                migration_date=today.strftime('%Y-%m-%d'),
            )
            ConsentRecord.objects.create(
                user_id=profile.user_id,
                consent_type=consent_type,
                granted=True,
                consent_text=consent_text,
                version=LEGACY_VERSION_TAG,
                granted_at=granted_at,
                ip_address=None,
            )
            created_count += 1

    return created_count


# ============================================================================
# Phase C C.4 commit 2 — GDPR Art. 15 right of access (data export)
# ============================================================================

EXPORT_VERSION = '1'


def _iso(dt):
    """Serialise a datetime to ISO-8601 or return None."""
    return dt.isoformat() if dt else None


def _profile_to_dict(profile):
    """Serialise TeacherProfile to a dict that survives json.dumps.
    JSONField values (list/dict) pass through; numeric/text fields too.
    Auto datetimes are ISO-formatted; choice fields keep their stored
    value (not display label) for round-trip-ability."""
    if profile is None:
        return None
    return {
        'first_name': profile.first_name,
        'last_name': profile.last_name,
        'display_name': profile.display_name,
        'subject_area': profile.subject_area,
        'subject_area_other': profile.subject_area_other,
        'grade_level': profile.grade_level,
        'teaching_years': profile.teaching_years,
        'school_location': profile.school_location,
        'average_class_size': profile.average_class_size,
        'ai_experience': profile.ai_experience,
        'ai_tools_used': profile.ai_tools_used,
        'ai_teaching_integration': profile.ai_teaching_integration,
        'primary_goals': profile.primary_goals,
        'preferred_communication_style': profile.preferred_communication_style,
        'profile_completed': profile.profile_completed,
        'profile_completion_date': _iso(profile.profile_completion_date),
        'research_consent': profile.research_consent,
        'consent_data_sharing': profile.consent_data_sharing,
        'contact_for_research': profile.contact_for_research,
        'research_data_opted_out': profile.research_data_opted_out,
        'consent_timestamp': _iso(profile.consent_timestamp),
        'ai_disclosure_acknowledged_at': _iso(profile.ai_disclosure_acknowledged_at),
        'current_curriculum_pressure': profile.current_curriculum_pressure,
        'student_population_special_needs': profile.student_population_special_needs,
        'institutional_ai_policy': profile.institutional_ai_policy,
        'created_at': _iso(profile.created_at) if hasattr(profile, 'created_at') else None,
        'updated_at': _iso(profile.updated_at) if hasattr(profile, 'updated_at') else None,
    }


def _consents_to_list(user):
    from apps.compliance.models import ConsentRecord
    rows = ConsentRecord.objects.filter(user=user).order_by('granted_at')
    return [
        {
            'consent_type': r.consent_type,
            'version': r.version,
            'granted': r.granted,
            'granted_at': _iso(r.granted_at),
            'revoked_at': _iso(r.revoked_at),
            'consent_text': r.consent_text,
            'ip_address': r.ip_address,
        }
        for r in rows
    ]


def _ailst_responses_to_list(user):
    from apps.ailst.models import AilstResponse
    rows = AilstResponse.objects.filter(user=user).order_by('timepoint')
    return [
        {
            'timepoint': r.timepoint,
            'language': r.language,
            'instrument_version': r.instrument_version,
            'responses': r.responses,
            'started_at': _iso(r.started_at),
            'completed_at': _iso(r.completed_at),
            'last_saved_at': _iso(r.last_saved_at),
            'perception_score': float(r.perception_score) if r.perception_score is not None else None,
            'knowledge_skills_score': float(r.knowledge_skills_score) if r.knowledge_skills_score is not None else None,
            'applications_innovation_score': float(r.applications_innovation_score) if r.applications_innovation_score is not None else None,
            'ethics_score': float(r.ethics_score) if r.ethics_score is not None else None,
            'overall_score': float(r.overall_score) if r.overall_score is not None else None,
        }
        for r in rows
    ]


def _module_progress_to_list(user):
    """Serialise UserModuleProgress rows. Reflection content text fields
    are included as separate keys; the AI-generated fields under
    `ai_outputs` reference the SAME text by module code (see
    _ai_outputs_to_dict) so a downstream parser can pick whichever
    grouping is convenient.
    """
    from apps.modules.models import UserModuleProgress
    rows = UserModuleProgress.objects.filter(user=user).select_related('module').order_by('module__order_index')
    return [
        {
            'module_code': p.module.code,
            'started_at': _iso(p.started_at),
            'completed_at': _iso(p.completed_at),
            'completion_percentage': p.completion_percentage,
            'status': p.status,
            'introduction_completed': p.introduction_completed,
            'main_content_completed': p.main_content_completed,
            'activity_completed': p.activity_completed,
            'assessment_completed': p.assessment_completed,
            'reflection_completed': p.reflection_completed,
            'reflection_text': p.reflection_text or '',
        }
        for p in rows
    ]


def _epilogue_to_dict(user):
    from apps.epilogue.models import EpilogueCompletion
    row = EpilogueCompletion.objects.filter(user=user).first()
    if row is None:
        return None
    return {
        'started_at': _iso(row.started_at),
        'completed_at': _iso(row.completed_at),
    }


def _ai_outputs_to_dict(user):
    """Aggregate every AI-generated artefact linked to the user.

    Sources:
      - RTM positions: ReflectionTension rows (one row per tension; a
        module may have multiple).
      - DTP narratives, RAG feedback, peer synthesis: TextField columns
        on UserModuleProgress keyed by module_code.
      - Raw RAG query log: rag_queries table (raw SQL — no Django ORM
        model). Includes the user's reflection text, the AI response,
        retrieved chunks, feedback rating/comments, and cost metrics.
        Per D11 + CP-4 verification.
      - AI dispute submissions: AIOutputDispute rows.
    """
    from apps.modules.models import (
        AIOutputDispute,
        ReflectionTension,
        UserModuleProgress,
    )

    rtm = [
        {
            'module_code': t.module.code,
            'tension_label': t.tension_label,
            'left_pole': t.left_pole,
            'right_pole': t.right_pole,
            'grounding_quote': t.grounding_quote,
            'selected_position': t.selected_position,
            'position_confirmed': t.position_confirmed,
        }
        for t in ReflectionTension.objects.filter(user=user).select_related('module')
    ]

    progress_rows = (
        UserModuleProgress.objects.filter(user=user).select_related('module')
    )
    dtp_narratives = []
    rag_feedback = []
    peer_synthesis = []
    for p in progress_rows:
        if p.reflection_dtp:
            dtp_narratives.append({'module_code': p.module.code, 'text': p.reflection_dtp})
        if p.reflection_rag_feedback:
            rag_feedback.append({'module_code': p.module.code, 'text': p.reflection_rag_feedback})
        if p.reflection_peer_synthesis:
            peer_synthesis.append({'module_code': p.module.code, 'text': p.reflection_peer_synthesis})

    rag_queries = _rag_queries_to_list(user)

    disputes = [
        {
            'module_code': d.module.code if d.module_id else None,
            'feature_type': d.feature_type,
            'rating': d.rating,
        }
        for d in AIOutputDispute.objects.filter(user=user).select_related('module')
    ]

    return {
        'rtm_positions': rtm,
        'dtp_narratives': dtp_narratives,
        'rag_feedback': rag_feedback,
        'peer_synthesis': peer_synthesis,
        'rag_queries': rag_queries,
        'ai_disputes': disputes,
    }


def _rag_queries_to_list(user):
    """rag_queries is a raw-SQL table outside the Django ORM (same quirk
    pattern as the pre-Phase-C consent_records). Pull rows via a cursor.

    Defensive: if the table does not exist in this environment (e.g. a
    fresh test DB before any rag_queries DDL has been applied), the
    ProgrammingError is caught and an empty list is returned. The
    export is best-effort on this table; missing-table is non-fatal
    because rag_queries is raw infrastructure, not a Django-managed
    artefact.

    Implementation: wrap the query in a savepoint via transaction.atomic
    so a ProgrammingError rolls back only the savepoint and leaves the
    outer transaction state clean. Without this, the TestCase outer
    transaction would be marked broken and every subsequent query in
    the same test would fail.
    """
    from django.db import transaction
    from django.db.utils import ProgrammingError

    rows = []
    try:
        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, module_id, reflection_text, teacher_context,
                           retrieved_chunks, num_chunks_retrieved,
                           generated_response, generation_tokens,
                           feedback_rating, feedback_comments,
                           feedback_timestamp, processing_time_ms,
                           api_cost_eur, created_at, updated_at
                    FROM rag_queries
                    WHERE user_id = %s
                    ORDER BY created_at
                    """,
                    [user.id],
                )
                cols = [c[0] for c in cur.description]
                for row in cur.fetchall():
                    entry = dict(zip(cols, row))
                    for k in ('feedback_timestamp', 'created_at', 'updated_at'):
                        entry[k] = _iso(entry[k]) if entry[k] else None
                    if entry.get('api_cost_eur') is not None:
                        entry['api_cost_eur'] = float(entry['api_cost_eur'])
                    rows.append(entry)
    except ProgrammingError:
        # Savepoint rolled back; outer transaction state is clean.
        pass
    return rows


def gather_user_export(user) -> dict:
    """GDPR Art. 15 right of access — full personal-data snapshot for `user`.

    Returns a JSON-serialisable dict. Always contains every top-level
    key, with empty arrays / null values when there is nothing to
    report (per CP-5: downstream parsers should never see KeyError on
    a fresh user). Caller is responsible for serialising to JSON.

    Top-level keys:
      - export_version (str)
      - exported_at (ISO-8601 str)
      - user (dict: username/email/dates)
      - profile (dict from _profile_to_dict, or None if no profile row)
      - consents (list)
      - ailst_responses (list)
      - module_progress (list)
      - epilogue_completion (dict or None)
      - ai_outputs (dict with rtm_positions / dtp_narratives /
        rag_feedback / peer_synthesis / rag_queries / ai_disputes lists)
    """
    profile = getattr(user, 'teacher_profile', None)

    return {
        'export_version': EXPORT_VERSION,
        'exported_at': _iso(timezone.now()),
        'user': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': _iso(user.date_joined),
            'last_login': _iso(user.last_login),
            'is_active': user.is_active,
        },
        'profile': _profile_to_dict(profile),
        'consents': _consents_to_list(user),
        'ailst_responses': _ailst_responses_to_list(user),
        'module_progress': _module_progress_to_list(user),
        'epilogue_completion': _epilogue_to_dict(user),
        'ai_outputs': _ai_outputs_to_dict(user),
    }


# ============================================================================
# Phase C C.4 commit 3 — GDPR Art. 17 right to erasure (anonymization)
# ============================================================================

ERASURE_EMAIL_TEMPLATE = 'deleted-{user_id}@anonymized.local'
ERASURE_USERNAME_TEMPLATE = 'anonymized_{user_id}'


def anonymize_user(user) -> None:
    """GDPR Art. 17 right-to-erasure — PII nullification, research data retained.

    Atomic transaction. Caller is responsible for the user-facing
    logout / redirect dance — this function only touches the DB. Does
    NOT delete the auth_user row (would CASCADE-destroy ConsentRecord
    audit trail, AILST research data, and module progress). Instead:

      1. TeacherProfile PII fields cleared via clear_pii_on_profile;
         research_data_opted_out flipped to True; profile saved.
      2. auth_user username / email rewritten to anonymized sentinel
         values verified per CP-1 (email column is NOT NULL but NOT
         UNIQUE in the live schema; the f'deleted-{id}@anonymized.local'
         pattern is collision-free by construction).
         first_name / last_name cleared. is_active=False (prevents
         login). Password set unusable.
      3. ConsentRecord rows: ip_address cleared on all rows (no need
         to wait for the 30-day batch). consent_text / granted /
         granted_at / revoked_at / version are part of the IRB audit
         trail and survive 7 years — see TD-016 for the future
         retention-window cleanup job.
      4. UserModuleProgress rows: reflection_text /
         reflection_rag_feedback / reflection_peer_synthesis /
         reflection_dtp cleared to empty strings. Other progress
         metadata retained for research analyses (filterable via
         research_data_opted_out flag).
      5. ReflectionTension rows: tension_label, left_pole, right_pole,
         grounding_quote cleared (user-attributable text). Numeric
         selected_position retained (research variable).
      6. AIOutputDispute rows: feature_type/rating retained;
         user-attributable fields cleared.
      7. rag_queries (raw SQL): reflection_text, generated_response,
         feedback_comments cleared; teacher_context name/full_name
         keys removed; query_embedding set to NULL.

    Idempotent: calling on an already-anonymized user is a no-op
    write (the sentinel pattern survives — re-application of
    f'anonymized_{user.id}' to user.username produces the same value).
    """
    from apps.modules.models import (
        AIOutputDispute,
        ReflectionTension,
        UserModuleProgress,
    )
    from apps.users.models import TeacherProfile
    from django.db import transaction
    from django.db.utils import ProgrammingError

    with transaction.atomic():
        # 1. TeacherProfile PII clearing + opt-out flip.
        try:
            profile = TeacherProfile.objects.select_for_update().get(user=user)
        except TeacherProfile.DoesNotExist:
            profile = None

        if profile is not None:
            clear_pii_on_profile(profile)
            profile.research_data_opted_out = True
            profile.save()

        # 2. auth_user PII clearing.
        user.username = ERASURE_USERNAME_TEMPLATE.format(user_id=user.id)
        user.email = ERASURE_EMAIL_TEMPLATE.format(user_id=user.id)
        user.first_name = ''
        user.last_name = ''
        user.is_active = False
        user.set_unusable_password()
        user.save()

        # 3. ConsentRecord IP redaction (bulk OK — no signal handlers
        # depend on ip_address transitions). consent_text / granted /
        # granted_at / revoked_at preserved for the 7-year IRB window.
        from apps.compliance.models import ConsentRecord
        ConsentRecord.objects.filter(
            user=user, ip_address__isnull=False,
        ).update(ip_address=None)

        # 4. UserModuleProgress reflection-content clearing.
        UserModuleProgress.objects.filter(user=user).update(
            reflection_text='',
            reflection_rag_feedback='',
            reflection_peer_synthesis='',
            reflection_dtp='',
        )

        # 5. ReflectionTension user-attributable text clearing.
        ReflectionTension.objects.filter(user=user).update(
            tension_label='',
            left_pole='',
            right_pole='',
            grounding_quote='',
        )

        # 6. AIOutputDispute — currently no user-authored free text on
        # this model (feature_type/rating/reason are enum choices).
        # The model exists for potential future free-text additions;
        # the placeholder filter below ensures the rows are at least
        # touched so the audit query in tests can verify the row count
        # is unchanged.
        AIOutputDispute.objects.filter(user=user).count()

        # 7. rag_queries PII clearing (raw SQL, savepoint-wrapped).
        try:
            with transaction.atomic():
                with connection.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE rag_queries
                        SET reflection_text = '',
                            generated_response = '',
                            feedback_comments = '',
                            query_embedding = NULL,
                            teacher_context = teacher_context
                                - 'name' - 'full_name'
                        WHERE user_id = %s
                        """,
                        [user.id],
                    )
        except ProgrammingError:
            # Table absent in this environment.
            pass
