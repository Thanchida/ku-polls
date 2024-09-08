import datetime
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from polls.models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'], [question])

    def test_status_display_for_published_question(self):
        """
        Test that correct status (Open) is displayed for published question.
        """
        create_question(question_text="Published question.", days=-1)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "Published question")
        self.assertContains(response, '<div class="open-status">Open</div>', html=True)

    def test_status_display_for_unpublished_question(self):
        """
        Test that correct status (Close) is displayed for unpublished question.
        """
        create_question(question_text="Published question.", days=10)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "Published question")
        self.assertContains(response, '<div class="close-status">Close</div>', html=True)

    def test_two_past_question(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'], [question2, question1])
