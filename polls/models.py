import datetime
from django.db import models
from django.utils import timezone


class Question(models.Model):
    """
    Display the polls question.

    Attributes:
        question_text (CharField): The text of question.
        pub_date (DateTimeField): The datetime when question published.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


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
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text



