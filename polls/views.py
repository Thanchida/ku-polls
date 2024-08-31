from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Question, Choice


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

    def get_only_published(self, request):
        question = self.get_object()
        if not question.is_published():
            return render(request, 'polls/detail.html',
                          {'error_message': "This question is not publish yet"})


class ResultsView(generic.DetailView):
    """
    The views that displays results of vote for each question.

    Attributes:
        model (Model): The model for question.
        template_name (str): The name of template to be used for this view.
    """
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    """
    Handle voting process for each question.
    :param request: The Http request object.
    :param question_id: The ID of the question.
    :return: Redirect to the result page
    """
    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        return render(request, 'polls/detail.html', {'question': question,
                                                     'error_message': "Voting is not allow now"})

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {'question': question,
                                                     'error_message': "You didn't select a choice",
                                                     })
    else:
        selected_choice.votes += 1
        selected_choice.save()
    return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))


