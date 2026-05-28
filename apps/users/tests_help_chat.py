"""View integration tests for help_chat_view (Phase J.1c).

Covers:
  - Auth guard: unauthenticated POST → 302
  - Method guard: GET → 405
  - Bad input: missing/empty question → 400, invalid JSON → 400
  - Happy path: valid question → 200 JSON {reply, turn_count, at_limit}
  - Session management: turns stored, turn_count increments per user message
  - Turn limit: 20-turn ceiling returns at_limit=True without agent call
  - API failure: HelpAgent returns None → graceful 200 with error reply
  - CSRF: endpoint is csrf_protect (standard Django test client sends CSRF)

HelpAgent.extract() is patched throughout — no live Gemini call.
"""

import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.users.models import TeacherProfile


_HELP_URL = '/help-chat/'
_REPLY = 'TAB5 is the Reflection tab — write about your experience and submit.'


def _make_user(username='helper', password='pass'):
    user = User.objects.create_user(username=username, password=password)
    TeacherProfile.objects.create(
        user=user,
        subject_area='mathematics',
        grade_level='secondary',
        ai_disclosure_acknowledged_at=timezone.now(),
        profile_completed=True,
    )
    return user


def _post_json(client, data):
    return client.post(
        _HELP_URL,
        data=json.dumps(data),
        content_type='application/json',
    )


class HelpChatAuthTest(TestCase):

    def test_unauthenticated_post_redirects(self):
        c = Client()
        resp = _post_json(c, {'question': 'What is TAB5?'})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp['Location'])

    def test_get_returns_405(self):
        user = _make_user()
        c = Client()
        c.force_login(user)
        resp = c.get(_HELP_URL)
        self.assertEqual(resp.status_code, 405)


class HelpChatValidationTest(TestCase):

    def setUp(self):
        self.user = _make_user()
        self.client.force_login(self.user)

    def test_empty_question_returns_400(self):
        resp = _post_json(self.client, {'question': '  '})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error'], 'empty_question')

    def test_missing_question_returns_400(self):
        resp = _post_json(self.client, {})
        self.assertEqual(resp.status_code, 400)

    def test_invalid_json_returns_400(self):
        resp = self.client.post(
            _HELP_URL,
            data='NOT JSON',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error'], 'invalid_request')


class HelpChatHappyPathTest(TestCase):

    def setUp(self):
        self.user = _make_user()
        self.client.force_login(self.user)

    def _post(self, question='What is the DTP?'):
        mock_agent = MagicMock()
        mock_agent.extract.return_value = _REPLY
        with patch('apps.agents.help_agent.HelpAgent', return_value=mock_agent):
            return _post_json(self.client, {'question': question}), mock_agent

    def test_returns_200_json(self):
        resp, _ = self._post()
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('reply', data)
        self.assertIn('turn_count', data)
        self.assertIn('at_limit', data)

    def test_reply_matches_agent_output(self):
        resp, _ = self._post()
        self.assertEqual(resp.json()['reply'], _REPLY)

    def test_at_limit_false_on_first_turn(self):
        resp, _ = self._post()
        self.assertFalse(resp.json()['at_limit'])

    def test_turn_count_is_one_after_first_question(self):
        resp, _ = self._post()
        self.assertEqual(resp.json()['turn_count'], 1)

    def test_agent_extract_called_with_question(self):
        _, mock_agent = self._post('Tell me about RTM.')
        mock_agent.extract.assert_called_once()
        call_kwargs = mock_agent.extract.call_args[1]
        self.assertEqual(call_kwargs['question'], 'Tell me about RTM.')

    def test_session_stores_two_turns_after_one_exchange(self):
        self._post()
        turns = self.client.session.get('help_turns', [])
        self.assertEqual(len(turns), 2)
        self.assertEqual(turns[0]['role'], 'user')
        self.assertEqual(turns[1]['role'], 'assistant')

    def test_second_question_passes_history_to_agent(self):
        mock_agent = MagicMock()
        mock_agent.extract.return_value = _REPLY
        with patch('apps.agents.help_agent.HelpAgent', return_value=mock_agent):
            _post_json(self.client, {'question': 'First question.'})
            _post_json(self.client, {'question': 'Second question.'})
        second_call_kwargs = mock_agent.extract.call_args_list[1][1]
        history = second_call_kwargs['history']
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['content'], 'First question.')

    def test_turn_count_increments_per_user_message(self):
        mock_agent = MagicMock()
        mock_agent.extract.return_value = _REPLY
        with patch('apps.agents.help_agent.HelpAgent', return_value=mock_agent):
            _post_json(self.client, {'question': 'Q1.'})
            resp = _post_json(self.client, {'question': 'Q2.'})
        self.assertEqual(resp.json()['turn_count'], 2)


class HelpChatTurnLimitTest(TestCase):

    def setUp(self):
        self.user = _make_user()
        self.client.force_login(self.user)

    def _seed_session_turns(self, n_exchanges):
        """Pre-populate the session with n_exchanges user+assistant pairs."""
        turns = []
        for i in range(n_exchanges):
            turns.append({'role': 'user', 'content': f'Question {i}'})
            turns.append({'role': 'assistant', 'content': f'Answer {i}'})
        session = self.client.session
        session['help_turns'] = turns
        session.save()

    def test_at_20_turns_returns_at_limit_true_without_agent_call(self):
        self._seed_session_turns(20)
        mock_agent = MagicMock()
        with patch('apps.agents.help_agent.HelpAgent', return_value=mock_agent):
            resp = _post_json(self.client, {'question': 'One more question.'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['at_limit'])
        mock_agent.extract.assert_not_called()

    def test_limit_reply_contains_contact_hint(self):
        self._seed_session_turns(20)
        with patch('apps.agents.help_agent.HelpAgent'):
            resp = _post_json(self.client, {'question': 'Extra question.'})
        self.assertIn('ihu.gr', resp.json()['reply'])

    def test_19_turns_still_processes(self):
        self._seed_session_turns(19)
        mock_agent = MagicMock()
        mock_agent.extract.return_value = _REPLY
        with patch('apps.agents.help_agent.HelpAgent', return_value=mock_agent):
            resp = _post_json(self.client, {'question': '20th question.'})
        self.assertEqual(resp.json()['reply'], _REPLY)
        self.assertTrue(resp.json()['at_limit'])


class HelpChatApiFailureTest(TestCase):

    def setUp(self):
        self.user = _make_user()
        self.client.force_login(self.user)

    def test_agent_none_returns_graceful_reply(self):
        mock_agent = MagicMock()
        mock_agent.extract.return_value = None
        with patch('apps.agents.help_agent.HelpAgent', return_value=mock_agent):
            resp = _post_json(self.client, {'question': 'Will fail.'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get('error'), 'api_failure')
        self.assertIn('unavailable', data['reply'])

    def test_agent_none_does_not_add_to_session_turns(self):
        mock_agent = MagicMock()
        mock_agent.extract.return_value = None
        with patch('apps.agents.help_agent.HelpAgent', return_value=mock_agent):
            _post_json(self.client, {'question': 'Will fail.'})
        turns = self.client.session.get('help_turns', [])
        self.assertEqual(len(turns), 0)
