import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_future_question_is_not_published(self):
        """
        Test that the 'is_published' method returns False for a question
        with a future publication date.
        """
        future_question = create_question(question_text='Future Question.', days=5)
        self.assertIs(future_question.is_published(), False)

    def test_past_question_is_published(self):
        """
        Test that the 'is_published' method returns True for a question
        with a past publication date.
        """
        past_question = create_question(question_text='Past Question', days=-5)
        self.assertIs(past_question.is_published(), True)

    def test_question_is_published(self):
        """
        Test that the 'is_published' method returns True for a question
        with a current publication date.
        """
        question = Question.objects.create(question_text='Question with default pub_date')
        self.assertIs(question.is_published(), True)

    def test_cannot_vote_before_pub_date(self):
        """
        Test that can_vote() return False for the question that has not been published yet.
        """
        question = create_question(question_text='Not publish question.', days=10)
        self.assertFalse(question.can_vote())

    def test_cannot_vote_after_end_date(self):
        """
        Test that can_vote() return False for voting after end_date.
        """
        pub_date = timezone.now() - timezone.timedelta(10)
        end_date = timezone.now() - timezone.timedelta(5)
        question = Question.objects.create(question_text='end of voting question.', pub_date=pub_date,
                                           end_date=end_date)
        self.assertFalse(question.can_vote())

    def test_can_vote_in_voting_period(self):
        """
        Test that can_vote() return True for vote in voting period.
        """
        pub_date = timezone.now() - timezone.timedelta(10)
        end_date = timezone.now() + timezone.timedelta(5)
        question = Question.objects.create(question_text='end of voting question.', pub_date=pub_date,
                                           end_date=end_date)
        self.assertTrue(question.can_vote())

    def test_can_vote_on_end_date(self):
        """
        Test that can_vote() returns True if the current time is exactly the end_date
        (the last moment to vote).
        """
        pub_date = timezone.now() - timezone.timedelta(10)
        end_date = (timezone.now() + timezone.timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0)
        question = Question.objects.create(question_text='Vote on end date.', pub_date=pub_date,
                                           end_date=end_date)
        self.assertTrue(question.can_vote())


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


class QuestionDetailViewTests(TestCase):
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
        self.assertContains(response, past_question.question_text)