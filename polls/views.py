from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Question, Choice, Vote
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
import logging


logger = logging.getLogger("polls")


class IndexView(generic.ListView):
    """
    Displays a list of the last five questions.

    Attributes:
        template_name (str): The name of template to be used for this view.
        context_object_name (str): The name of context to be used in the template.
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions.
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """
    A view that displays details of each question.

    Attributes:
        model (Model): The model for question.
        template_name (str): The name of template to be used for this view.
    """
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs):
        try:
            question = Question.objects.get(pk=self.kwargs['pk'])
        except Question.DoesNotExist as ex:
            logger.exception(f"Non-existent question {self.kwargs['pk']} %s", ex)
            messages.error(request, f'No question found with ID {self.kwargs["pk"]}.')
            return redirect(reverse('polls:index'))

        if not question.is_published():
            messages.error(request, 'This question is not yet published.')
            return redirect(reverse('polls:index'))

        if not question.can_vote():
            messages.error(request, 'This poll is closed.')
            return redirect(reverse('polls:index'))

        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        messages.error(request, "Voting requires you to be logged in.")
        return redirect(reverse('login'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()
        try:
            user_vote = Vote.objects.get(user=self.request.user, choice__question=question)
        except Vote.DoesNotExist:
            user_vote = None
        context['user_vote'] = user_vote
        return context


class ResultsView(generic.DetailView):
    """
    The views that displays results of vote for each question.

    Attributes:
        model (Model): The model for question.
        template_name (str): The name of template to be used for this view.
    """
    model = Question
    template_name = 'polls/results.html'


@login_required
def vote(request, question_id):
    """
    Handle voting process for each question.
    :param request: The Http request object.
    :param question_id: The ID of the question.
    :return: Redirect to the result page
    """
    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        messages.error(request, "Voting is not allowed now")
        return HttpResponseRedirect(reverse('polls:detail', args=(question_id,)))

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {'question': question,
                                                     'error_message': "You didn't select a choice",
                                                     })

    this_user = request.user
    try:
        vote = Vote.objects.get(user=this_user, choice__question=question)
        vote.choice = selected_choice
        vote.save()
        messages.success(request, f"Your vote was changed to '{selected_choice.choice_text}'")
        logger.info(
            f"{this_user.username} changed vote for question_id {question_id} to choice_id {selected_choice.id} "
            f"from {get_client_ip(request)}")
    except Vote.DoesNotExist:
        vote = Vote.objects.create(user=this_user, choice=selected_choice)
        messages.success(request, f"You voted for '{selected_choice.choice_text}'")
        logger.info(f"{this_user.username} submitted a vote for question_id {question_id} "
                    f"choice_id {selected_choice.id} from {get_client_ip(request)}")

    return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip_address = get_client_ip(request)
    logger.info(f'User {user.username} logged in from {ip_address}')


@receiver(user_logged_out)
def log_user_login(sender, request, user, **kwargs):
    ip_address = get_client_ip(request)
    logger.info(f'User {user.username} logged out from {ip_address}')


@receiver(user_login_failed)
def log_failed_login(sender, request, credentials, **kwargs):
    ip_address = get_client_ip(request)
    username = credentials.get('username', 'unknown')
    logger.warning(f'User {username} login failed from {ip_address}')
