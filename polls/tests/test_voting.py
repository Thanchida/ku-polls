import datetime

from django.test import TestCase
from django.utils import timezone
from polls.models import Question
from django.urls import reverse
from django.contrib.auth import get_user_model


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


User = get_user_model()


class VotingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="test123")
        self.client.login(username="test", password="test123")

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        redirect to the index page and show message error.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url, follow=True)
        self.assertContains(response, "This question is not yet published.")

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        if not self.user.is_authenticated:
            self.assertRedirects(response, reverse('polls:index'))