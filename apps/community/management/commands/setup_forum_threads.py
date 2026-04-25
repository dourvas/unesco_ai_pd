"""
apps/community/management/commands/setup_forum_threads.py
==========================================================
Management command to create ForumThread for each published module
and seed M1 with the researcher's opening questions.

Usage:
    python manage.py setup_forum_threads
    python manage.py setup_forum_threads --seed-m1
    python manage.py setup_forum_threads --module M1
"""

from django.core.management.base import BaseCommand
from django.apps import apps


# Seeded questions per module (researcher-defined)
SEEDED_QUESTIONS = {
    'M1': {
        'title': 'Discussion: Understanding AI in Education',
        'q1': (
            'How do you feel about integrating AI into your teaching? '
            'What inspires you and what concerns you?'
        ),
        'q2': (
            'Have you already used an AI tool in your classroom? '
            'Share an experience — positive or negative!'
        ),
    },
    'M2': {
        'title': 'Discussion: AI & Human-Centric Approach',
        'q1': 'What does "human-centric AI" mean to you in an educational context?',
        'q2': '',
    },
    'M3': {
        'title': 'Discussion: Ethics of AI in Education',
        'q1': 'Which ethical dilemma regarding AI in education concerns you the most?',
        'q2': 'How do you explain the limits and responsibilities of AI use to your students?',
    },
}


class Command(BaseCommand):
    help = 'Create ForumThread for each published module and seed with discussion questions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--module',
            type=str,
            help='Create/update thread for a specific module code only (e.g. M1)',
        )
        parser.add_argument(
            '--seed-m1',
            action='store_true',
            help='Force re-seed M1 questions even if thread already exists',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Create threads for ALL modules (including unpublished)',
        )

    def handle(self, *args, **options):
        Module = apps.get_model('modules', 'Module')
        ForumThread = apps.get_model('community', 'ForumThread')

        # Filter modules
        if options.get('module'):
            modules = Module.objects.filter(code=options['module'].upper())
            if not modules.exists():
                self.stdout.write(self.style.ERROR(f"Module {options['module']} not found."))
                return
        elif options.get('all'):
            modules = Module.objects.all().order_by('order_index')
        else:
            modules = Module.objects.filter(is_published=True).order_by('order_index')

        created_count = 0
        updated_count = 0

        for module in modules:
            seed_data = SEEDED_QUESTIONS.get(module.code, {})
            title = seed_data.get('title', f'Discussion: {module.title}')
            q1 = seed_data.get('q1', '')
            q2 = seed_data.get('q2', '')

            thread, created = ForumThread.objects.get_or_create(
                module=module,
                defaults={
                    'title': title,
                    'seeded_question': q1,
                    'seeded_question_2': q2,
                    'is_active': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created thread for {module.code}: "{title}"')
                )
            else:
                # Update title and questions if seed data available
                if options.get('seed_m1') or seed_data:
                    thread.title = title
                    if q1:
                        thread.seeded_question = q1
                    if q2:
                        thread.seeded_question_2 = q2
                    thread.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↺ Updated thread for {module.code}')
                    )
                else:
                    self.stdout.write(f'  Thread for {module.code} already exists (skipped)')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! Created: {created_count}, Updated: {updated_count}'
        ))

        if created_count > 0 or updated_count > 0:
            self.stdout.write('')
            self.stdout.write('Next steps:')
            self.stdout.write('  1. Add community/ URLs to config/urls.py')
            self.stdout.write('  2. Include quick_post_modal.html in base.html')
            self.stdout.write('  3. Add tab triggers to module_detail.html')