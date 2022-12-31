from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from .models import *
from html import unescape


def del_q_marks(request, topic, test):
    user = request.user
    test_id = test
    test = Quiz.objects.filter(id=test).first()
    q_marks = QuestionMark.objects.filter(user=user).filter(question__quiz__name=test)
    q_marks.delete()
    return HttpResponseRedirect(reverse('quiz:start_test', args=[topic, test_id]))


class StartView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        topics = Topic.objects.exclude(trash_bin=True)
        return render(request, 'start_new.html', {'topics': topics, 'user': user})


class TestsView(View):
    def get(self, request, topic):
        user = request.user
        topic = Topic.objects.filter(id=topic).first()
        tests = Quiz.objects.filter(topic=topic)
        return render(request, 'tests.html', {'topic': topic, 'tests': tests, 'user': user})


class StartTestView(View):
    def get(self, request, topic, test):
        user = request.user
        test_id = test
        topic_obj = Topic.objects.filter(id=topic).first()
        test = Quiz.objects.filter(id=test).first()
        questions = Question.objects.filter(quiz=test).order_by('id')
        q_marks = QuestionMark.objects.filter(user=user).filter(question__quiz__name=test)
        for q in questions:
            try:
                q_marks.filter(question=q).filter(user=user)[0:1].get()
                continue
            except QuestionMark.DoesNotExist:
                options = q.option_set.filter(question=q)
                for option in options:
                    option.answer_text = unescape(option.answer_text)
                return render(request, 'question.html', {'topic': topic, 'topic_obj': topic_obj, 'test': test, 'question': q.text, 'options': options, 'q_id': q.id})
        return HttpResponseRedirect(reverse('quiz:test_res', args=[topic, test_id]))

    def post(self, request, topic, test):
        user = request.user
        test_id = test
        test = Quiz.objects.filter(id=test).first()
        q_id = request.POST['q_id']
        question = Question.objects.filter(id=q_id).first()
        user_answer = request.POST.getlist('answers')
        mark = QuestionMark.objects.create(user=user, question=question, done_correct=False, user_answer=user_answer)
        return HttpResponseRedirect(reverse('quiz:start_test', args=[topic, test_id]))


class ResultTestView(View):
    def get(self, request, topic, test):
        user = request.user
        topic_obj = Topic.objects.filter(id=topic).first()
        test_obj = Quiz.objects.filter(id=test).first()
        try:
            QuestionMark.objects.filter(user=user).filter(question__quiz__name=test_obj).filter(processed=False)[0:1].get()
            q_marks = QuestionMark.objects.filter(user=user).filter(question__quiz__name=test_obj)
            if q_marks.count() == Question.objects.filter(quiz=test_obj).count():
                corr_count = q_marks.filter(done_correct=True).count()
                wrong_count = q_marks.count() - corr_count
                score = str(round((corr_count/q_marks.count() * 100), 2)) + '%'
                date = datetime.now()
                TestMark.objects.create(user=user, topic=topic_obj.name, quiz=test_obj.name, score=score, date=date)
                t_mark = TestMark.objects.filter(user=user).filter(quiz=test_obj.name).filter(date=date).first()
                q_marks_wrong = q_marks.filter(done_correct=False)
                for i in q_marks_wrong:
                    ErrorObject.objects.create(user=user, question=i.question, test_mark=t_mark, test_date=date, wrong_answers=i.user_answer)
                q_marks.update(processed=True)
                return render(request, 'result.html', {'test': test_obj, 'marks': q_marks, 'score': score, 'wrong': wrong_count, 'correct': corr_count, 'date': date})
            else:
                topic_obj = Topic.objects.filter(id=topic).first()
                tests = Quiz.objects.filter(id=test)
                return render(request, 'error.html', {'topic': topic, 'topic_obj': topic_obj, 'tests': tests})
        except QuestionMark.DoesNotExist:
            topic_obj = Topic.objects.filter(id=topic).first()
            tests = Quiz.objects.filter(id=test)
            return render(request, 'error.html', {'topic': topic, 'topic_obj': topic_obj, 'tests': tests})



class HistoryTopicView(View):
    def get(self, request, topic):
        user = request.user
        topic_obj = Topic.objects.filter(id=topic).first()
        qs = TestMark.objects.filter(user=user).filter(topic=topic_obj).order_by('quiz', '-date')
        return render(request, 'history.html', {'topic': topic_obj, 'attempts': qs})


class HistoryAllTopicView(View):
    def get(self, request):
        user = request.user
        qs = TestMark.objects.filter(user=user).order_by('quiz', '-date')
        return render(request, 'history_all.html', {'attempts': qs})

