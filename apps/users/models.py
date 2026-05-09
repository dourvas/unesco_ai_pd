"""
User and Teacher Profile Models
UNESCO AI Teacher PD Platform - v2.2.0
Updated: January 2026 - International English version
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class TeacherProfile(models.Model):
    """
    Extended profile for teachers with comprehensive onboarding data.
    Linked 1:1 with Django User model.
    
    Version: 2.2.0 - International English version with 16 subjects
    """
    
    # === CORE RELATIONSHIP ===
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name="User"
    )

    # ============================================================
    # PERSONAL INFORMATION
    # For certificate generation and personalized feedback
    # International-friendly naming system
    # ============================================================
    first_name = models.CharField(
        max_length=100,
        verbose_name="First Name",
        help_text="Your first/given name (required for certificate)",
        blank=True,  # Allow blank initially for existing users
        default=''
    )
    
    last_name = models.CharField(
        max_length=100,
        verbose_name="Last Name",
        help_text="Your family name/surname (required for certificate)",
        blank=True,
        default=''
    )
    
    display_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name="Display Name (Optional)",
        help_text="Leave blank to use 'First Last'. Use this for patronymics, middle names, or cultural naming conventions (e.g., 'Ιωάννης Δούρβας του Γεωργίου')"
    )
    
    @property
    def full_name(self):
        """
        Return the complete name for display.
        Priority: display_name > first_name + last_name > username
        """
        if self.display_name:
            return self.display_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.user.username
    
    @property
    def certificate_name(self):
        """Name to appear on certificates (same as full_name)"""
        return self.full_name
    
    # === STEP 1: TEACHING CONTEXT ===
    
    SUBJECT_CHOICES = [
        ('mathematics', 'Mathematics'),
        ('language_arts', 'Language Arts / English'),
        ('science', 'Science (General)'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('social_studies', 'Social Studies'),
        ('history', 'History'),
        ('geography', 'Geography'),
        ('foreign_languages', 'World Languages'),
        ('computer_science', 'Computer Science / ICT'),
        ('physical_education', 'Physical Education & Health'),
        ('arts', 'Arts'),
        ('special_education', 'Special Education'),
        ('early_childhood', 'Early Childhood Education'),
        ('other', 'Primary Teacher / General Education'),
    ]
    
    subject_area = models.CharField(
        max_length=50,
        choices=SUBJECT_CHOICES,
        blank=True,
        null=True,
        verbose_name="Subject Area",
        help_text="Your primary teaching subject"
    )
    
    subject_area_other = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Other Subject",
        help_text="If you selected 'Other', please specify"
    )
    
    GRADE_LEVEL_CHOICES = [
        ('kindergarten', 'Kindergarten / Pre-K'),
        ('primary', 'Primary / Elementary (1-6)'),
        ('lower_secondary', 'Lower Secondary / Middle School (7-9)'),
        ('upper_secondary', 'Upper Secondary / High School (10-12)'),
        ('university', 'University / Higher Education'),
    ]
    
    grade_level = models.CharField(
        max_length=20,
        choices=GRADE_LEVEL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Grade Level",
        help_text="Which grade level do you primarily teach?"
    )
    
    TEACHING_YEARS_CHOICES = [
        ('0-5', '0-5 years'),
        ('6-15', '6-15 years'),
        ('16-25', '16-25 years'),
        ('25+', '25+ years'),
    ]
    
    teaching_years = models.CharField(
        max_length=10,
        choices=TEACHING_YEARS_CHOICES,
        blank=False,
        null=True,
        verbose_name="Years of Teaching Experience"
    )
    
    LOCATION_CHOICES = [
        ('urban', 'Urban Area'),
        ('suburban', 'Suburban Area'),
        ('rural', 'Rural / Remote Area'),
    ]
    
    school_location = models.CharField(
        max_length=20,
        choices=LOCATION_CHOICES,
        blank=False,
        null=True,
        verbose_name="School Location"
    )
    
    CLASS_SIZE_CHOICES = [
        ('small', 'Small (<15 students)'),
        ('medium', 'Medium (15-25 students)'),
        ('large', 'Large (26-35 students)'),
        ('very_large', 'Very Large (>35 students)'),
    ]
    
    average_class_size = models.CharField(
        max_length=20,
        choices=CLASS_SIZE_CHOICES,
        blank=False,
        null=True,
        verbose_name="Average Class Size"
    )
    
    # === STEP 2: AI EXPERIENCE ===
    
    AI_EXPERIENCE_CHOICES = [
        ('none', 'None - First time with AI'),
        ('basic', 'Basic - Have tried ChatGPT/AI tools'),
        ('intermediate', 'Intermediate - Use AI regularly'),
        ('advanced', 'Advanced - Integrate AI in teaching'),
    ]
    
    ai_experience = models.CharField(
        max_length=20,
        choices=AI_EXPERIENCE_CHOICES,
        default='none',
        verbose_name="AI Experience Level"
    )
    
    ai_tools_used = models.JSONField(
        default=list,
        blank=True,
        verbose_name="AI Tools Used",
        help_text="List of AI tools (e.g., ['ChatGPT', 'Gemini', 'Claude'])"
    )
    
    ai_teaching_integration = models.TextField(
        blank=True,
        verbose_name="How do you use AI in teaching?",
        help_text="Brief description - 100-200 words"
    )
    
    # === STEP 3: PREFERENCES & GOALS ===
    
    # Learning goals stored as JSON array
    primary_goals = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Primary Learning Goals",
        help_text="Top 3 goals"
    )
    
    COMMUNICATION_STYLE_CHOICES = [
        ('concise', 'Concise - Key points only'),
        ('detailed', 'Detailed - Extended explanations'),
        ('balanced', 'Balanced - Mix of both'),
    ]
    
    preferred_communication_style = models.CharField(
        max_length=20,
        choices=COMMUNICATION_STYLE_CHOICES,
        default='balanced',
        verbose_name="Preferred Communication Style"
    )
    
    # === METADATA ===
    
    profile_completed = models.BooleanField(
        default=False,
        verbose_name="Profile Completed"
    )
    
    profile_completion_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Profile Completion Date"
    )
    
    profile_skipped = models.BooleanField(
        default=False,
        verbose_name="User skipped onboarding"
    )
    
    last_profile_update = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Update"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    # === RESEARCH & ANALYTICS ===
    
    research_consent = models.BooleanField(
        default=True,
        verbose_name="Consent to use data for research"
    )
    
    contact_for_research = models.BooleanField(
        default=False,
        verbose_name="Available for research interviews"
    )
    
    consent_data_sharing = models.BooleanField(
        default=False,
        verbose_name="Consent to data sharing"
    )
    
    consent_timestamp = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Consent Timestamp"
    )
    
    # === OPTIONAL DEMOGRAPHICS ===
    
    age_range = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Age Range"
    )
    
    gender = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Gender"
    )
    
    language_primary = models.CharField(
        max_length=50,
        blank=True,
        default='en',
        verbose_name="Primary Language"
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Admin notes - internal use only"
    )

    # === PHASE A TIER 3 — Practice Workshop ===
    BLOG_FILTER_CHOICES = [
        ('my_subject', 'My subject only'),
        ('adjacent', 'Adjacent subjects'),
        ('all', 'All subjects'),
    ]

    blog_subject_filter_preference = models.CharField(
        max_length=20,
        choices=BLOG_FILTER_CHOICES,
        default='adjacent',
        verbose_name="Practice Workshop subject filter",
        help_text="User's preferred Workshop feed filter mode (persisted across sessions).",
    )

    # === PHASE C — EU AI Act + Personalization (May 2026) ===

    ai_disclosure_acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="AI Disclosure Acknowledged At",
        help_text="Timestamp of acknowledgment of the EU AI Act Article 50 disclosure modal."
    )

    CURRICULUM_PRESSURE_CHOICES = [
        ('low', 'Low - flexible curriculum'),
        ('medium', 'Medium - standard pacing'),
        ('high', 'High - strict curriculum coverage demands'),
        ('variable', 'Variable - depends on term / class'),
    ]

    current_curriculum_pressure = models.CharField(
        max_length=20,
        choices=CURRICULUM_PRESSURE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Current Curriculum Pressure",
        help_text="Workload context for personalised, workload-aware AI feedback."
    )

    student_population_special_needs = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Student Population Special Needs",
        help_text=(
            "Multi-select. Allowed values: learning_disability, behavioural_support, "
            "physical_disability, language_minority, gifted, socioeconomic_disadvantage, none. "
            "'none' is exclusive (cannot be combined with other values)."
        )
    )

    INSTITUTIONAL_AI_POLICY_CHOICES = [
        ('none', 'No policy'),
        ('restrictive', 'Restrictive - AI use discouraged'),
        ('permissive', 'Permissive - AI use allowed'),
        ('explicit_supportive', 'Explicit and supportive - AI use encouraged'),
        ('unknown', 'I do not know'),
    ]

    institutional_ai_policy = models.CharField(
        max_length=30,
        choices=INSTITUTIONAL_AI_POLICY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Institutional AI Policy",
        help_text="School/institutional stance on AI use; informs M11/M12 contextual prompts."
    )

    # === COMPUTED PROPERTIES ===
    
    @property
    def completion_percentage(self):
        """Calculate profile completion percentage"""
        required_fields = [
            self.subject_area,
            self.grade_level,
            self.teaching_years,
            self.ai_experience
        ]
        
        optional_fields = [
            self.school_location,
            self.average_class_size,
            bool(self.primary_goals),
            self.preferred_communication_style
        ]
        
        required_complete = sum(1 for field in required_fields if field)
        optional_complete = sum(1 for field in optional_fields if field)
        
        # 60% weight for required, 40% for optional
        required_pct = (required_complete / len(required_fields)) * 60
        optional_pct = (optional_complete / len(optional_fields)) * 40
        
        return int(required_pct + optional_pct)
    
    @property
    def personalization_ready(self):
        """Check if minimum data for personalization exists"""
        return bool(self.subject_area and self.grade_level)
    
    @property
    def profile_summary(self):
        """Human-readable profile summary"""
        if not self.personalization_ready:
            return "Profile incomplete"

        subject = dict(self.SUBJECT_CHOICES).get(self.subject_area, self.subject_area)
        grade = dict(self.GRADE_LEVEL_CHOICES).get(self.grade_level, self.grade_level)

        return f"{subject} - {grade}"

    @property
    def pseudonym(self):
        """
        GDPR-friendly display name for community / Practice Workshop posts.
        Returns display_name if set, otherwise f"Educator_{user.id}".
        Tier 3 — Blocker 1 Option B (no DB column, computed only).
        """
        if self.display_name:
            return self.display_name
        return f"Educator_{self.user_id}"
    
    def __str__(self):
        return f"{self.user.username} - {self.profile_summary}"
    
    class Meta:
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"
        ordering = ['-created_at']
        db_table = 'teacher_profiles'