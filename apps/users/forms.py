"""
Onboarding Forms - UNESCO AI Teacher PD Platform
3-Step Progressive Onboarding System
Version: 2.2.0 - International English version
"""

from django import forms
from .models import TeacherProfile


# Update TeachingContextForm in apps/users/forms.py
# Add name fields to Step 1

class TeachingContextForm(forms.ModelForm):
    """Step 1: Teaching Context + Personal Information"""
    
    # Override choice fields to customize the empty option
    grade_level = forms.ChoiceField(
        widget=forms.RadioSelect(),
        required=False,
        label="Grade Level"
    )
    
    teaching_years = forms.ChoiceField(
        widget=forms.RadioSelect(),
        required=False,
        label="Years of Teaching Experience"
    )
    
    school_location = forms.ChoiceField(
        widget=forms.RadioSelect(),
        required=False,
        label="School Location"
    )
    
    average_class_size = forms.ChoiceField(
        widget=forms.RadioSelect(),
        required=False,
        label="Average Class Size"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get choices directly from model fields (WITHOUT adding empty option)
        grade_choices = self._meta.model._meta.get_field('grade_level').choices
        self.fields['grade_level'].choices = list(grade_choices)

        teaching_years_choices = self._meta.model._meta.get_field('teaching_years').choices
        self.fields['teaching_years'].choices = list(teaching_years_choices)

        school_location_choices = self._meta.model._meta.get_field('school_location').choices
        self.fields['school_location'].choices = list(school_location_choices)

        class_size_choices = self._meta.model._meta.get_field('average_class_size').choices
        self.fields['average_class_size'].choices = list(class_size_choices)
    
    class Meta:
        model = TeacherProfile
        fields = [
            'first_name',
            'last_name',
            'display_name',
            'subject_area',
            'subject_area_other',
            'grade_level',
            'teaching_years',
            'school_location',
            'average_class_size',
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g., John',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g., Smith',
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Optional: "Dr. Jane Smith" ',
            }),
            'subject_area': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'subject_area_other': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            # Note: grade_level, teaching_years, school_location, average_class_size
            # are defined above as ChoiceFields with RadioSelect
        }
        
        labels = {
            'first_name': 'First Name *',
            'last_name': 'Last Name *',
            'display_name': 'Display Name (Optional)',
            'subject_area': 'Subject Area *',
            'subject_area_other': 'Please Specify Your Subject',
        }
        
        help_texts = {
            'first_name': 'Your given/first name',
            'last_name': 'Your family name/surname',
            'display_name': 'Leave blank to use "First Last". Use this for patronymics, middle names, or how you prefer your name displayed.',
        }
    
    def clean(self):
        """Validate form data"""
        cleaned_data = super().clean()
        
        # Validate names are provided
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if not first_name or not last_name:
            raise forms.ValidationError(
                'Please provide your first and last name for certificate generation.'
            )
        
        # Validate subject_area_other when subject_area is 'other'
        subject_area = cleaned_data.get('subject_area')
        subject_area_other = cleaned_data.get('subject_area_other')
        
        if subject_area == 'other' and not subject_area_other:
            raise forms.ValidationError(
                'Please specify your subject area.'
            )
        
        return cleaned_data


class AIExperienceForm(forms.ModelForm):
    """
    Step 2: AI Experience
    Information about AI familiarity and usage
    """
    
    # Multi-select for AI tools (custom field, stored as JSON)
    ai_tools_checkboxes = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'checkbox checkbox-primary'
        }),
        choices=[
            ('ChatGPT', 'ChatGPT'),
            ('Gemini', 'Gemini (Google)'),
            ('Claude', 'Claude (Anthropic)'),
            ('Copilot', 'Microsoft Copilot'),
            ('MagicSchool', 'MagicSchool AI'),
            ('Eduaide', 'Eduaide'),
            ('Brisk', 'Brisk Teaching'),
            ('Canva AI', 'Canva (AI features)'),
            ('Other', 'Other')
        ],
        label="Which AI tools have you used?"
    )
    
    class Meta:
        model = TeacherProfile
        fields = [
            'ai_experience',
            'ai_teaching_integration'
        ]
        
        widgets = {
            'ai_experience': forms.RadioSelect(attrs={
                'class': 'radio radio-primary',
                'required': True
            }),
            'ai_teaching_integration': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'e.g. "I use AI to create exercises, provide feedback on assignments..."',
                'maxlength': 500
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove blank choice from ai_experience
        self.fields['ai_experience'].empty_label = None
        self.fields['ai_experience'].required = True
        
        # Pre-populate ai_tools_checkboxes from JSON field
        if self.instance.pk and self.instance.ai_tools_used:
            self.initial['ai_tools_checkboxes'] = self.instance.ai_tools_used
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Convert checkbox selections to JSON array
        ai_tools = self.cleaned_data.get('ai_tools_checkboxes', [])
        instance.ai_tools_used = list(ai_tools)
        
        if commit:
            instance.save()
        
        return instance


class GoalsPreferencesForm(forms.ModelForm):
    """
    Step 3: Goals & Preferences
    Learning objectives and communication style
    """
    
    # Multi-select for goals (custom field, stored as JSON)
    goals_checkboxes = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'checkbox checkbox-primary'
        }),
        choices=[
            ('understand_ai', 'Understand AI fundamentals'),
            ('practical_tools', 'Practical tools for the classroom'),
            ('ethical_use', 'Ethical & responsible AI use'),
            ('student_engagement', 'Increase student engagement'),
            ('differentiation', 'Differentiated instruction'),
            ('assessment', 'Assessment & feedback'),
            ('content_creation', 'Create educational materials'),
            ('leadership', 'Leadership & mentoring colleagues')
        ],
        label="What are your main goals? (select up to 3)"
    )
    
    class Meta:
        model = TeacherProfile
        fields = [
            'preferred_communication_style',
            'research_consent',
            'contact_for_research'
        ]
        
        widgets = {
            'preferred_communication_style': forms.RadioSelect(attrs={
                'class': 'radio radio-primary'
            }),
            'research_consent': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'contact_for_research': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remove blank choice
        self.fields['preferred_communication_style'].empty_label = None
        
        # Pre-populate goals_checkboxes from JSON field
        if self.instance.pk and self.instance.primary_goals:
            self.initial['goals_checkboxes'] = self.instance.primary_goals
    
    def clean_goals_checkboxes(self):
        goals = self.cleaned_data.get('goals_checkboxes', [])
        
        # Limit to 3 goals
        if len(goals) > 3:
            raise forms.ValidationError(
                'Please select up to 3 goals.'
            )
        
        return goals
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Convert checkbox selections to JSON array
        goals = self.cleaned_data.get('goals_checkboxes', [])
        instance.primary_goals = list(goals)
        
        if commit:
            instance.save()
        
        return instance


class ProfileEditForm(forms.ModelForm):
    """
    Complete profile edit form (all fields in one form)
    Used for editing after onboarding completion
    """
    
    # Custom multi-select fields
    ai_tools_checkboxes = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[
            ('ChatGPT', 'ChatGPT'),
            ('Gemini', 'Gemini (Google)'),
            ('Claude', 'Claude (Anthropic)'),
            ('Copilot', 'Microsoft Copilot'),
            ('MagicSchool', 'MagicSchool AI'),
            ('Eduaide', 'Eduaide'),
            ('Brisk', 'Brisk Teaching'),
            ('Canva AI', 'Canva (AI features)'),
            ('Other', 'Other')
        ],
        label="AI tools used"
    )
    
    goals_checkboxes = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[
            ('understand_ai', 'Understand AI'),
            ('practical_tools', 'Practical tools'),
            ('ethical_use', 'Ethical use'),
            ('student_engagement', 'Student engagement'),
            ('differentiation', 'Differentiation'),
            ('assessment', 'Assessment'),
            ('content_creation', 'Content creation'),
            ('leadership', 'Leadership')
        ],
        label="Learning goals"
    )
    
    class Meta:
        model = TeacherProfile
        fields = [
            'subject_area',
            'subject_area_other',
            'grade_level',
            'teaching_years',
            'school_location',
            'average_class_size',
            'ai_experience',
            'ai_teaching_integration',
            'preferred_communication_style',
            'research_consent',
            'contact_for_research'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-populate from JSON fields
        if self.instance.pk:
            if self.instance.ai_tools_used:
                self.initial['ai_tools_checkboxes'] = self.instance.ai_tools_used
            if self.instance.primary_goals:
                self.initial['goals_checkboxes'] = self.instance.primary_goals
    
    def clean_goals_checkboxes(self):
        goals = self.cleaned_data.get('goals_checkboxes', [])
        if len(goals) > 3:
            raise forms.ValidationError('Maximum 3 goals allowed.')
        return goals
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Save multi-select fields as JSON
        instance.ai_tools_used = list(self.cleaned_data.get('ai_tools_checkboxes', []))
        instance.primary_goals = list(self.cleaned_data.get('goals_checkboxes', []))
        
        if commit:
            instance.save()
        
        return instance