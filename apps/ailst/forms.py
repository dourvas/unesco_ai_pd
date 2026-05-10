"""
Forms for the AILST instrument administration views.

A single dynamic form class generates one TypedChoiceField per AILST
item on the requested page. Field names equal the paper_code (P1, K10,
A3 etc.) so cleaned_data can be merged directly into the
AilstResponse.responses JSONB dict.
"""

from django import forms
from django.utils.translation import gettext_lazy as _


# Five-point Likert anchors, descending so the strongest endorsement
# (value=5) appears first. Wording is paper-verbatim per CP 5; do not
# abbreviate (anchors are part of the validated instrument).
LIKERT_CHOICES = [
    (5, _('Fully applicable')),
    (4, _('Applicable')),
    (3, _('Uncertain')),
    (2, _('Not applicable')),
    (1, _('Completely not applicable')),
]


class AilstPageForm(forms.Form):
    """Dynamic form: one TypedChoiceField per item on the requested page.

    Field name == AilstItem.paper_code (P1, K10, A3 etc.). Field value
    type is coerced to int (1-5). All fields are required: skipping any
    item invalidates the instrument's measurement.
    """

    def __init__(self, *args, items=None, existing_responses=None, **kwargs):
        super().__init__(*args, **kwargs)
        existing_responses = existing_responses or {}
        for item in items or []:
            self.fields[item.paper_code] = forms.TypedChoiceField(
                choices=LIKERT_CHOICES,
                widget=forms.RadioSelect,
                coerce=int,
                required=True,
                label=item.item_text,
                error_messages={
                    'required': _('Please answer this item before continuing.'),
                },
                initial=existing_responses.get(item.paper_code),
            )
