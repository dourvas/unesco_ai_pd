from django.contrib import admin

from apps.compliance.models import AIArtefactProvenance


@admin.register(AIArtefactProvenance)
class AIArtefactProvenanceAdmin(admin.ModelAdmin):
    """Staff-only inspection surface for AI provenance records.

    Read-mostly. No edit/add/delete in admin (write paths flow through
    `record_ai_provenance` and the backfill command, never the admin).
    """

    list_display = (
        'artefact_kind',
        'artefact_pk',
        'user',
        'module',
        'model_name',
        'generated_at',
    )
    list_filter = ('artefact_kind', 'model_name', 'module')
    search_fields = ('user__username', 'prompt_hash')
    readonly_fields = (
        'artefact_kind', 'artefact_pk', 'user', 'module',
        'model_name', 'generated_at', 'prompt_hash', 'created_at',
    )
    ordering = ('-generated_at',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
