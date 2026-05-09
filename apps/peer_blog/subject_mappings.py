"""
Hand-curated adjacent-subjects mapping for blog feed filtering.
Tier 3 — May 2026, v3 (Gemini D11 + D13).

Each subject maps to:
  'subjects': list of subject_areas to include in 'adjacent' mode
  'rationales': dict mapping each adjacent subject to a pedagogical rationale
                (used by 'Why these?' modal in UI)

Mapping is intuitive (no formal taxonomy); revisit based on pilot data.
"""

ADJACENT_SUBJECTS = {
    'mathematics': {
        'subjects': ['mathematics', 'science', 'physics', 'computer_science'],
        'rationales': {
            'science': 'Both rely on AI for hypothesis exploration and data modelling',
            'physics': 'Shared mathematical reasoning and problem-solving patterns',
            'computer_science': 'Algorithmic thinking common to both domains',
        },
    },
    'language_arts': {
        'subjects': ['language_arts', 'foreign_languages', 'social_studies'],
        'rationales': {
            'foreign_languages': 'Both work with text generation, comprehension, and language structure',
            'social_studies': 'Critical reading and source evaluation transfer between domains',
        },
    },
    'science': {
        'subjects': ['science', 'mathematics', 'physics', 'biology', 'chemistry'],
        'rationales': {
            'mathematics': 'Both rely on AI for hypothesis exploration and data modelling',
            'physics': 'Both apply scientific method with AI-assisted experimentation',
            'biology': 'Both use AI for pattern recognition in natural systems',
            'chemistry': 'Both work with AI tools for molecular and process visualisation',
        },
    },
    'physics': {
        'subjects': ['physics', 'mathematics', 'science', 'chemistry'],
        'rationales': {
            'mathematics': 'Shared mathematical reasoning and problem-solving patterns',
            'science': 'Both apply scientific method with AI-assisted experimentation',
            'chemistry': 'Both involve AI-assisted modelling of physical phenomena',
        },
    },
    'chemistry': {
        'subjects': ['chemistry', 'science', 'physics', 'biology'],
        'rationales': {
            'science': 'Both work with AI tools for molecular and process visualisation',
            'physics': 'Both involve AI-assisted modelling of physical phenomena',
            'biology': 'Both apply AI to molecular and biochemical analysis',
        },
    },
    'biology': {
        'subjects': ['biology', 'science', 'chemistry', 'physical_education'],
        'rationales': {
            'science': 'Both use AI for pattern recognition in natural systems',
            'chemistry': 'Both apply AI to molecular and biochemical analysis',
            'physical_education': 'Both connect biology to human movement and health',
        },
    },
    'social_studies': {
        'subjects': ['social_studies', 'language_arts', 'history', 'geography'],
        'rationales': {
            'language_arts': 'Critical reading and source evaluation transfer between domains',
            'history': 'Both engage AI in source analysis and narrative construction',
            'geography': 'Both apply AI to spatial and contextual reasoning',
        },
    },
    'history': {
        'subjects': ['history', 'social_studies', 'geography', 'language_arts'],
        'rationales': {
            'social_studies': 'Both engage AI in source analysis and narrative construction',
            'geography': 'Both connect events to places and contexts',
            'language_arts': 'Both work with primary text analysis and interpretation',
        },
    },
    'geography': {
        'subjects': ['geography', 'social_studies', 'history', 'science'],
        'rationales': {
            'social_studies': 'Both apply AI to spatial and contextual reasoning',
            'history': 'Both connect events to places and contexts',
            'science': 'Both use AI for environmental and earth-system analysis',
        },
    },
    'foreign_languages': {
        'subjects': ['foreign_languages', 'language_arts'],
        'rationales': {
            'language_arts': 'Both work with text generation, comprehension, and language structure',
        },
    },
    'arts': {
        'subjects': ['arts', 'language_arts', 'early_childhood'],
        'rationales': {
            'language_arts': 'Both engage AI in creative expression and narrative',
            'early_childhood': 'Both prioritise developmental and creative pedagogy',
        },
    },
    'physical_education': {
        'subjects': ['physical_education', 'biology', 'early_childhood'],
        'rationales': {
            'biology': 'Both connect biology to human movement and health',
            'early_childhood': 'Both apply movement-based pedagogy with developmental focus',
        },
    },
    'early_childhood': {
        'subjects': [
            'early_childhood',
            'arts',
            'language_arts',
            'physical_education',
            'special_education',
        ],
        'rationales': {
            'arts': 'Both prioritise developmental and creative pedagogy',
            'language_arts': 'Both build foundational literacy with AI scaffolds',
            'physical_education': 'Both apply movement-based pedagogy with developmental focus',
            'special_education': 'Both centre individualised learner needs',
        },
    },
    'special_education': {
        'subjects': ['special_education', 'early_childhood', 'language_arts'],
        'rationales': {
            'early_childhood': 'Both centre individualised learner needs',
            'language_arts': 'Both adapt AI to communication and literacy support',
        },
    },
    'computer_science': {
        'subjects': ['computer_science', 'mathematics'],
        'rationales': {
            'mathematics': 'Algorithmic thinking common to both domains',
        },
    },
    'other': {
        'subjects': ['other'],  # Conservative fallback — same only
        'rationales': {},
    },
}


def get_filtered_subjects(user_subject, mode):
    """
    Return list of subject_areas to include in blog feed based on user's mode.

    Args:
        user_subject: User's primary subject_area (str), may be None
        mode: 'my_subject', 'adjacent', or 'all'

    Returns:
        list of subject_area strings, or None for 'all' (no filter)
    """
    if mode == 'all':
        return None
    if not user_subject:
        return None  # Profile incomplete — show all rather than block
    if mode == 'my_subject':
        return [user_subject]
    if mode == 'adjacent':
        config = ADJACENT_SUBJECTS.get(user_subject, {})
        return config.get('subjects', [user_subject])
    return [user_subject]


def get_adjacency_rationales(user_subject):
    """
    Return rationales dict for the user's subject in adjacent mode.
    Used by the 'Why these?' modal in the blog UI.
    """
    if not user_subject:
        return {}
    config = ADJACENT_SUBJECTS.get(user_subject, {})
    return config.get('rationales', {})
