import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """
    Display the polls question.

    Attributes:
        question_text (CharField): The text of question.
        pub_date (DateTimeField): The datetime when question published.
        end_date (DateTimeField): The ending date for voting.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('ending date for voting', null=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        current_time = timezone.localtime(timezone.now())
        return current_time >= self.pub_date

    def can_vote(self):
        current_time = timezone.localtime(timezone.now())
        if self.end_date is None:
            return current_time >= self.pub_date
        return self.pub_date <= current_time <= self.end_date


class Choice(models.Model):
    """
    Display a choices for polls question.

    Attributes:
        question (ForeignKey): The question that choice belong to.
        choice_text (CharField): The text of choices.
        votes (IntegerField): The number of total votes.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    @property
    def votes(self):
        """returns the votes of the choice"""
        return self.vote_set.all().count()

    def __str__(self):
        return str(self.choice_text) if self.choice_text is not None else ''


class Vote(models.Model):
    """A vote by a user for a choice in a poll"""
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


