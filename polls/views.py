from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Question, Choice, Vote


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
        return Question.objects.order_by('-pub_date')[:5]


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
        question = Question.objects.get(pk=self.kwargs['pk'])
        if not question.is_published():
            messages.error(request, 'This question is not yet published.')
            return redirect(reverse('polls:index'))
        return super().get(request, *args, **kwargs)

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
    except Vote.DoesNotExist:
        vote = Vote.objects.create(user=this_user, choice=selected_choice)
        messages.success(request, f"You voted for '{selected_choice.choice_text}'")

    return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))


