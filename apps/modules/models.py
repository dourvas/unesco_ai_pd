from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid


class Module(models.Model):
    """
    UNESCO AI Competency Framework Module
    Stores metadata for 15 modules (M1-M15)
    
    Tab 1 (Introduction) content comes from this model's fields
    """
    
    # Identity
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Module code (M1, M2, ..., M15)"
    )
    
    # UNESCO Alignment
    unesco_aspect = models.CharField(
        max_length=50,
        choices=[
            ('human_centered', 'Human-Centred Mindset'),
            ('ethics', 'Ethics'),
            ('ai_foundations', 'AI Foundations'),
            ('ai_pedagogy', 'AI Pedagogy'),
            ('professional_development', 'Professional Development'),
        ],
        help_text="UNESCO AI CFT Aspect (1-5)"
    )
    
    proficiency_level = models.CharField(
        max_length=20,
        choices=[
            ('Acquire', 'Acquire'),
            ('Deepen', 'Deepen'),
            ('Create', 'Create'),
        ],
        help_text="UNESCO Proficiency Level"
    )
    
    # Basic Info
    title = models.CharField(
        max_length=200,
        help_text="Module title (English)"
    )
    description = models.TextField(
        help_text="Brief description (2-3 sentences)"
    )
    
    # Ordering
    order_index = models.IntegerField(
        unique=True,
        help_text="Display order (1-15)"
    )
    estimated_hours = models.IntegerField(
        default=4,
        help_text="Estimated completion time in hours"
    )
    
    # Tab 1 (Introduction) Content
    hero_image_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Hero image URL or static path"
    )
    learning_objectives = models.JSONField(
        default=list,
        help_text="Array of learning objectives (4-6 items)"
    )
    module_overview = models.TextField(
        blank=True,
        help_text="Module overview text for Tab 1 (100-200 words)"
    )
    prerequisites = models.JSONField(
        default=list,
        help_text="Array of required module IDs: [1, 2, 3]"
    )
    
    # Publishing
    is_published = models.BooleanField(
        default=False,
        help_text="Module visible to users"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order_index']
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
    
    def __str__(self):
        return f"{self.code}: {self.title}"
    
    def get_absolute_url(self):
        return reverse('modules:detail', kwargs={'code': self.code})
    
    def get_next_module(self):
        """Get next published module in sequence"""
        return Module.objects.filter(
            order_index__gt=self.order_index,
            is_published=True
        ).first()
    
    def get_previous_module(self):
        """Get previous published module in sequence"""
        return Module.objects.filter(
            order_index__lt=self.order_index,
            is_published=True
        ).order_by('-order_index').first()

    def get_vertical_predecessor(self):
        """Return the module one UNESCO proficiency level below this one
        within the same aspect, or None when this module is at the base
        (Acquire) level.

        Used by the DTP Vertical Continuity Signal: a Deepen module pairs
        with its Acquire counterpart, a Create module with its Deepen
        counterpart. Acquire modules have no vertical predecessor. See
        proodos_files/DTP_REDEFINITION_DESIGN_PROPOSAL_v1_20260518.md.
        """
        proficiency_order = ('Acquire', 'Deepen', 'Create')
        try:
            level_index = proficiency_order.index(self.proficiency_level)
        except ValueError:
            return None
        if level_index == 0:
            return None
        return Module.objects.filter(
            unesco_aspect=self.unesco_aspect,
            proficiency_level=proficiency_order[level_index - 1],
            is_published=True,
        ).first()
    
    @property
    def completion_rate(self):
        """Calculate module completion rate across all users"""
        total_started = UserModuleProgress.objects.filter(module=self).count()
        if total_started == 0:
            return 0
        
        total_completed = UserModuleProgress.objects.filter(
            module=self,
            completed_at__isnull=False
        ).count()
        
        return round((total_completed / total_started) * 100, 1)


class ModuleContent(models.Model):
    """
    Dynamic content for Tabs 2-5 with personalization support
    """
    
    # Relations
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    
    # Content Type
    CONTENT_TYPE_CHOICES = [
        ('main_content', 'Κύριο Περιεχόμενο'),
        ('activity', 'Δραστηριότητα'),
        ('assessment', 'Αξιολόγηση'),
        ('reflection', 'Αναστοχασμός'),
    ]
    
    content_type = models.CharField(
        max_length=50,
        choices=CONTENT_TYPE_CHOICES,
        help_text="Content tab type"
    )
    
    # Personalization
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
    
    GRADE_CHOICES = [
        ('kindergarten', 'Kindergarten / Pre-K'),
        ('primary', 'Primary / Elementary (1-6)'),
        ('lower_secondary', 'Lower Secondary / Middle School (7-9)'),
        ('upper_secondary', 'Upper Secondary / High School (10-12)'),
        ('university', 'University / Higher Education'),
    ]
    
    subject_area = models.CharField(
        max_length=50,
        choices=SUBJECT_CHOICES,
        default='Universal'
    )
    
    grade_level = models.CharField(
        max_length=50,
        choices=GRADE_CHOICES,
        default='All'
    )
    
    # Content
    content_data = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['module__order_index', 'content_type']
        verbose_name = 'Module Content'
        verbose_name_plural = 'Module Contents'
        unique_together = ('module', 'content_type', 'subject_area', 'grade_level')
    
    def __str__(self):
        variant = ""
        if self.subject_area != 'Universal':
            variant += f" [{self.subject_area}]"
        if self.grade_level != 'All':
            variant += f" [{self.grade_level}]"
        return f"{self.module.code} - {self.get_content_type_display()}{variant}"


class UserModuleProgress(models.Model):
    """
    Track user progress through a module (5 tabs)
    """
    
    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='user_progress')
    
    # Status
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('enrolled', 'Enrolled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    # Timestamps
    enrolled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)
    
    # Progress
    completion_percentage = models.IntegerField(default=0)
    
    # Tab Completion Flags
    introduction_completed = models.BooleanField(default=False)
    introduction_completed_at = models.DateTimeField(null=True, blank=True)
    main_content_completed = models.BooleanField(default=False)
    main_content_completed_at = models.DateTimeField(null=True, blank=True)
    activity_completed = models.BooleanField(default=False)
    activity_completed_at = models.DateTimeField(null=True, blank=True)
    assessment_completed = models.BooleanField(default=False)
    assessment_completed_at = models.DateTimeField(null=True, blank=True)
    reflection_completed = models.BooleanField(default=False)
    reflection_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Reflection data (RAG system) ← NEW!
    reflection_text = models.TextField(null=True, blank=True)
    reflection_rag_feedback = models.TextField(null=True, blank=True)

    reflection_peer_synthesis = models.TextField(null=True, blank=True)
    reflection_dtp = models.TextField(blank=True, null=True)

    # D.3b — the XAIAgent natural-language explanation of the DTP
    # composite above. Written by XAIAgent.generate(); see
    # proodos_files/DTP_XAI_NARRATIVE_DESIGN_PROPOSAL_v1_20260519.md.
    reflection_dtp_xai = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('user', 'module')
        ordering = ['-last_accessed_at']
        verbose_name = 'User Module Progress'
        verbose_name_plural = 'User Module Progress'
    
    def __str__(self):
        return f"{self.user.username} - {self.module.code} ({self.completion_percentage}%)"
    
    @property
    def current_tab(self):
        """Determine which tab user should be on"""
        if not self.introduction_completed:
            return 'introduction'
        elif not self.main_content_completed:
            return 'main_content'
        elif not self.activity_completed:
            return 'activity'
        elif not self.assessment_completed:
            return 'assessment'
        elif not self.reflection_completed:
            return 'reflection'
        return 'completed'
    
    @property
    def unlock_status(self):
        """Return dict of tab unlock status"""
        return {
            'introduction': True,
            'main_content': self.introduction_completed,
            'activity': self.main_content_completed,
            'assessment': self.activity_completed,
            'reflection': self.assessment_completed,
        }
    
    def calculate_completion_percentage(self):
        """Calculate completion percentage"""
        completed = sum([
            self.introduction_completed,
            self.main_content_completed,
            self.activity_completed,
            self.assessment_completed,
            self.reflection_completed,
        ])
        return int((completed / 5) * 100)
    
    def mark_tab_complete(self, tab_name, **kwargs):
        """Mark tab as completed"""
        from django.utils import timezone
        
        if tab_name == 'introduction':
            self.introduction_completed = True
            self.introduction_completed_at = timezone.now()
            if not self.started_at:
                self.started_at = timezone.now()
                self.status = 'in_progress'
        
        elif tab_name == 'main_content':
            self.main_content_completed = True
            self.main_content_completed_at = timezone.now()
        
        elif tab_name == 'activity':
            self.activity_completed = True
            self.activity_completed_at = timezone.now()
        
        elif tab_name == 'assessment':
            score = kwargs.get('score', 0)
            if score >= 80:
                self.assessment_completed = True
                self.assessment_completed_at = timezone.now()
            else:
                raise ValueError(f"Score {score}% below 80% threshold")
        
        elif tab_name == 'reflection':
            # Store reflection text and RAG feedback ← UPDATED!
            self.reflection_text = kwargs.get('reflection_text', '')
            self.reflection_rag_feedback = kwargs.get('rag_feedback', '')
            
            self.reflection_completed = True
            self.reflection_completed_at = timezone.now()
            
            if all([self.introduction_completed, self.main_content_completed,
                    self.activity_completed, self.assessment_completed,
                    self.reflection_completed]):
                self.completed_at = timezone.now()
                self.status = 'completed'
        
        self.completion_percentage = self.calculate_completion_percentage()
        self.save()
        return self.current_tab
# apps/modules/models.py - TAB 3 Models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ============================================================================
# TAB 3: PROMPT LIBRARY
# ============================================================================

class Tab3PromptLibrary(models.Model):
    """
    Library of pre-built prompts for different subjects and types
    """
    PROMPT_TYPES = [
        ('good', 'Good Prompt (Challenge 1)'),
        ('bad', 'Bad Prompt (Challenge 2)'),
        ('lesson_plan', 'Lesson Plan Generator'),
        ('quiz', 'Quiz/Assessment Creator'),
        ('differentiation', 'Differentiation Helper'),
    ]
    
    SUBJECTS = [
        ('Mathematics', 'Mathematics'),
        ('Greek Language', 'Greek Language'),
        ('Science', 'Science'),
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Biology', 'Biology'),
        ('Computer Science', 'Computer Science'),
        ('History', 'History'),
        ('Geography', 'Geography'),
        ('Foreign Languages', 'Foreign Languages'),
        ('Physical Education', 'Physical Education'),
        ('Arts & Music', 'Arts & Music'),
        ('Special Education', 'Special Education'),
        ('Early Childhood', 'Early Childhood'),
        ('Other', 'Primary Teacher / General Education'),
    ]
    
    subject = models.CharField(max_length=50, choices=SUBJECTS)
    grade_level = models.CharField(max_length=20, blank=True, null=True)
    prompt_type = models.CharField(max_length=50, choices=PROMPT_TYPES)
    prompt_template = models.TextField(
        help_text="Use {{topic}} and {{grade}} as placeholders"
    )
    example_topic = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tab3_prompt_library'
        verbose_name = 'TAB 3 Prompt'
        verbose_name_plural = 'TAB 3 Prompt Library'
        indexes = [
            models.Index(fields=['subject', 'prompt_type']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.get_prompt_type_display()}"


# ============================================================================
# TAB 3: USER ACTIVITY
# ============================================================================

class Tab3UserActivity(models.Model):
    """
    Generic TAB 3 activity tracker — works for all modules (M1-M15).
    Module-specific challenge data stored in challenge_data JSONB field.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module_id = models.IntegerField(default=1)

    # Challenge completion flags (generic across all modules)
    challenge1_completed = models.BooleanField(default=False)
    challenge1_completed_at = models.DateTimeField(null=True, blank=True)

    challenge2_completed = models.BooleanField(default=False)
    challenge2_completed_at = models.DateTimeField(null=True, blank=True)

    challenge3_completed = models.BooleanField(default=False)
    challenge3_completed_at = models.DateTimeField(null=True, blank=True)

    reflection_completed = models.BooleanField(default=False)
    reflection_completed_at = models.DateTimeField(null=True, blank=True)

    activity_completed = models.BooleanField(default=False)
    activity_completed_at = models.DateTimeField(null=True, blank=True)

    # All module-specific challenge data (M1-M15)
    challenge_data = models.JSONField(default=dict, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tab3_user_activity'
        verbose_name = 'TAB 3 User Activity'
        verbose_name_plural = 'TAB 3 User Activities'
        unique_together = ['user', 'module_id']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['activity_completed']),
        ]

    def __str__(self):
        return f"{self.user.username} - TAB 3 Activity (module_id={self.module_id})"

    def completion_percentage(self):
        """Calculate completion percentage"""
        completed = sum([
            self.challenge1_completed,
            self.challenge2_completed,
            self.challenge3_completed,
            self.reflection_completed
        ])
        return (completed / 4) * 100


# ============================================================================
# TAB 3: USER TOOLKIT
# ============================================================================

class Tab3UserToolkit(models.Model):
    """
    Store prompts and results that users save to their toolkit
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    prompt_text = models.TextField()
    ai_result = models.TextField(blank=True)
    tool_used = models.CharField(max_length=50, blank=True)
    
    subject = models.CharField(max_length=50, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    prompt_type = models.CharField(max_length=50, blank=True)
    
    rating = models.IntegerField(null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tab3_user_toolkit'
        verbose_name = 'TAB 3 Toolkit Item'
        verbose_name_plural = 'TAB 3 Toolkit Items'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.prompt_type or 'Toolkit Item'}"
class Assessment(models.Model):
    """Quiz/assessment attempts and scores"""
    module = models.ForeignKey('Module', on_delete=models.CASCADE, related_name='assessments')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    score = models.IntegerField(help_text="Number of correct answers")
    max_score = models.IntegerField(default=15)
    passed = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)
    answers = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assessments'
        unique_together = [['module', 'teacher']]
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.teacher.email} - {self.module.code} - {self.score}/{self.max_score}"
    
    @property
    def percentage(self):
        return round((self.score / self.max_score) * 100, 1) if self.max_score > 0 else 0

# ============================================================================
# TAB 5: REFLECTIVE TENSION MAPPER (RTM)
# ============================================================================

class ReflectionTension(models.Model):
    """
    Epistemic positioning data from Reflective Tension Mapper (RTM).
    Stores AI-extracted pedagogical tensions and user's self-positioning responses.
    
    Research use: Quantifies implicit beliefs, enables longitudinal belief-shift analysis.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    position_confirmed = models.BooleanField(default=False)
    
    # Foreign Keys
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reflection_tensions'
    )
    module = models.ForeignKey(
        'Module',
        on_delete=models.CASCADE,
        related_name='reflection_tensions'
    )
    # reflection FK reserved for future RAGQuery integration
    # reflection = models.ForeignKey('RAGQuery', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Tension Definition (from AI extraction - audit trail)
    tension_label = models.CharField(
        max_length=100,
        help_text="Short label (max 6 words) identifying the tension"
    )
    left_pole = models.TextField(
        help_text="Left pole description grounded in teacher's wording"
    )
    right_pole = models.TextField(
        help_text="Right pole description grounded in teacher's wording"
    )
    grounding_quote = models.TextField(
        help_text="Verbatim quote from reflection supporting this tension (audit trail)"
    )
    
    # User Response
    selected_position = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="User self-positioning: 1=strongly left pole, 5=strongly right pole"
    )
    optional_comment = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="User's optional explanation for their positioning (max 150 chars)"
    )
    
    # Research Metadata
    time_spent_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Milliseconds user spent interacting with RTM card"
    )
    comment_used = models.BooleanField(
        default=False,
        help_text="Whether user added an optional comment"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reflection_tensions'
        unique_together = [['user', 'module', 'tension_label']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['module']),
            models.Index(fields=['tension_label']),
            models.Index(fields=['selected_position']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['created_at']
        verbose_name = 'Reflection Tension'
        verbose_name_plural = 'Reflection Tensions'
    
    def __str__(self):
        return f"{self.user.username} - {self.module.code} - {self.tension_label}"
    
    @property
    def position_label(self):
        """Human-readable position label for research reporting."""
        labels = {
            1: 'Strongly Left',
            2: 'Leaning Left',
            3: 'Neutral / Middle',
            4: 'Leaning Right',
            5: 'Strongly Right'
        }
        return labels.get(self.selected_position, 'Unknown')

# ============================================================
# AIOutputDispute Model
# Add to apps/modules/models.py
# ============================================================
# Run after adding:
#   python manage.py makemigrations modules
#   python manage.py migrate

class AIOutputDispute(models.Model):
    """
    Human-in-the-Loop feedback on AI outputs in TAB5.

    Two distinct constructs share this table — keep them apart in analysis:

    - 'rag', 'rtm', 'dtp' — the **AI alignment instrument**. Each of these
      AI outputs makes a claim about the teacher's own reflection, so the
      rating ('yes'/'partial'/'no' relevant) is a proxy for whether the AI
      read the teacher correctly. Only these three feed the D.1 perceived-
      relevance profile; the D.1 aggregation must whitelist them explicitly.
    - 'peer' — a **usefulness signal**, not part of the alignment
      instrument. Peer synthesis makes no claim about the teacher; it
      aggregates anonymised peer reflections. The rating here answers
      "did you find this synthesis useful?" — a different construct
      (TD-019, redefined 2026-05-19). Excluded from the D.1 profile.

    EU AI Act: operationalises meaningful human oversight requirement.
    """

    FEATURE_CHOICES = [
        ('rag', 'RAG Feedback'),
        ('rtm', 'Reflective Tension Mapper'),
        ('dtp', 'Developmental Trajectory Predictor'),
        # Usefulness signal, not alignment — see class docstring (TD-019).
        ('peer', 'Peer Synthesis'),
    ]

    RATING_CHOICES = [
        ('yes', 'Relevant'),
        ('no', 'Not relevant'),
        ('partial', 'Partially relevant'),
    ]

    REASON_CHOICES = [
        ('mismatch', 'Does not match my subject context'),
        ('misinterpretation', 'AI misunderstood my reflection'),
        ('generic', 'Too generic / low value'),
        ('pedagogical', 'Pedagogical disagreement'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='ai_disputes'
    )
    module = models.ForeignKey(
        'Module',
        on_delete=models.CASCADE,
        related_name='ai_disputes'
    )
    feature_type = models.CharField(
        max_length=10,
        choices=FEATURE_CHOICES
    )
    rating = models.CharField(
        max_length=10,
        choices=RATING_CHOICES
    )
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        blank=True,
        null=True
    )
    comment = models.TextField(
        max_length=300,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One rating per user per feature per module
        unique_together = ('user', 'module', 'feature_type')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['feature_type', 'rating']),
            models.Index(fields=['module', 'feature_type']),
            models.Index(fields=['user', 'module']),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.get_feature_type_display()} — {self.module.code} — {self.rating}"


# ============================================================
# Tab3RepositorySubmission — Phase A Tier 2 Step 4 (M13 patch)
# Stores user submissions to the curated PROODOS Verified Repository
# from M13 Challenge 2 (Hybrid Workflow Canvas).
# ============================================================
class Tab3RepositorySubmission(models.Model):
    """
    Submissions from M13 Challenge 2 (Hybrid Workflow Canvas) to the
    curated PROODOS Verified Repository. Reviewed by master teachers
    via Django admin. UNESCO indicators: LO3.3.4, CA3.3.3.
    """

    REVIEW_STATUS_CHOICES = [
        # Phase A Tier 3: 'community_shared' is the active state for new submissions.
        # Workflow no longer gates by curated approval — content visible immediately
        # in the M13 Practice Workshop. See REACTIVE_MODERATION_POLICY.md.
        ('community_shared', 'Community Shared (Practice Workshop)'),
        # Legacy curation states retained for historical submissions.
        ('pending', 'Pending Peer Review (legacy)'),
        ('approved', 'Approved (legacy)'),
        ('rejected', 'Rejected (legacy)'),
        ('needs_revision', 'Needs Revision (legacy)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    challenge_id = models.IntegerField(default=2)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=200)
    subject_area = models.CharField(max_length=50)
    grade_level = models.CharField(max_length=20)
    contact_email = models.EmailField(blank=True)
    canvas_data = models.JSONField(default=dict, blank=True)
    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default='pending',
    )
    reviewer_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        related_name='reviewed_submissions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'TAB3 Repository Submission'
        verbose_name_plural = 'TAB3 Repository Submissions'
        indexes = [
            models.Index(fields=['review_status', '-submitted_at']),
            models.Index(fields=['module', 'review_status']),
        ]

    def __str__(self):
        return f"{self.title} — {self.user.username} — {self.module.code} ({self.review_status})"