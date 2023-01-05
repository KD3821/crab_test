from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from .models import *
from html import unescape
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


@login_required
def del_q_marks(request, topic, test):
    user = request.user
    test_obj = Quiz.objects.filter(id=test).first()
    q_marks = QuestionMark.objects.filter(user=user).filter(question__quiz__name=test_obj)
    q_marks.delete()
    return HttpResponseRedirect(reverse('quiz:start_test', args=[topic, test]))


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


class StartTestView(LoginRequiredMixin, View):
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
                return render(request, 'question.html', {'topic': topic, 'topic_obj': topic_obj, 'test': test,
                                                         'question': q.text, 'options': options, 'q_id': q.id})
        return HttpResponseRedirect(reverse('quiz:test_res', args=[topic, test_id]))

    def post(self, request, topic, test):
        user = request.user
        test_id = test
        test = Quiz.objects.filter(id=test).first()
        q_id = request.POST['q_id']
        question = Question.objects.filter(id=q_id).first()
        user_answer = request.POST.getlist('answers')
        QuestionMark.objects.create(user=user, question=question, done_correct=False, user_answer=user_answer)
        return HttpResponseRedirect(reverse('quiz:start_test', args=[topic, test_id]))


class ResultTestView(LoginRequiredMixin, View):
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
                # date = datetime.now()
                date = timezone.now()
                TestMark.objects.create(user=user, topic=topic_obj.name, quiz=test_obj.name, score=score, date=date)
                t_mark = TestMark.objects.filter(user=user).filter(quiz=test_obj.name).filter(date=date).first()
                q_marks_wrong = q_marks.filter(done_correct=False)
                for i in q_marks_wrong:
                    ErrorObject.objects.create(user=user, question=i.question, test_mark=t_mark, test_date=date, wrong_answers=i.user_answer)
                q_marks.update(processed=True)
                user_answer_dict = {}
                corr_answer_dict = {}
                for qm in q_marks:
                    usr_ans_list = []
                    tmp_u_ans_list = qm.user_answer.strip("[]").split(",")
                    for i in tmp_u_ans_list:
                        usr_ans_list.append(int(i.strip().strip("''")))
                    usr_ans_qs = Option.objects.filter(id__in=usr_ans_list).order_by('id')
                    for i in usr_ans_qs:
                        i.answer_text = unescape(i.answer_text)
                    user_answer_dict[qm] = usr_ans_qs
                    cor_ans_qs = Option.objects.filter(question=qm.question).filter(is_correct=True).order_by('id')
                    for i in cor_ans_qs:
                        i.answer_text = unescape(i.answer_text)
                    corr_answer_dict[qm] = cor_ans_qs
                return render(request, 'result.html', {'test': test, 'topic': topic, 'test_obj': test_obj,
                                                       'marks': q_marks, 'score': score, 'wrong': wrong_count,
                                                       'correct': corr_count, 'date': date, 'u_a_dict': user_answer_dict,
                                                       'c_a_dict': corr_answer_dict})
            else:
                topic_obj = Topic.objects.filter(id=topic).first()
                tests = Quiz.objects.filter(id=test)
                return render(request, 'error.html', {'topic': topic, 'topic_obj': topic_obj, 'tests': tests})
        except QuestionMark.DoesNotExist:
            topic_obj = Topic.objects.filter(id=topic).first()
            tests = Quiz.objects.filter(id=test)
            return render(request, 'error.html', {'topic': topic, 'topic_obj': topic_obj, 'tests': tests})


@login_required
def view_errors(request, test_mark):
    user = request.user
    mark = TestMark.objects.filter(id=test_mark).first()
    topic_name = mark.topic
    topic_obj = Topic.objects.filter(name=topic_name).first()
    test_name = mark.quiz
    test_obj = Quiz.objects.filter(name=test_name).first()
    tests = Quiz.objects.filter(topic=topic_obj)
    try:
        ErrorObject.objects.filter(user=user).filter(test_mark=test_mark)[0:1].get()
        errors = ErrorObject.objects.filter(user=user).filter(test_mark=test_mark)
        errors_dict = {}
        for e in errors:
            compare_dict = {}
            cor_qs = e.question.option_set.filter(is_correct=True)
            for i in cor_qs:
                i.answer_text = unescape(i.answer_text)
            tmp_e_list = e.wrong_answers
            e_list_ok = []
            e_list = tmp_e_list.strip("[]").split(",")
            for i in e_list:
                e_list_ok.append(int(i.strip().strip("''")))
            err_qs = Option.objects.filter(id__in=e_list_ok)
            for i in err_qs:
                i.answer_text = unescape(i.answer_text)
            compare_dict['cor'] = cor_qs
            compare_dict['err'] = err_qs
            errors_dict[e] = compare_dict
        total_q_count = test_obj.question_set.count()
        err_q_count = errors.count()
        cor_q_count = total_q_count - err_q_count
        return render(request, 'mistakes.html', {'topic': topic_obj, 'test': test_obj, 'mark': mark, 'errors': errors,
                                                 'errors_dict': errors_dict, 'cor_count': cor_q_count,
                                                 'err_count': err_q_count})
    except ErrorObject.DoesNotExist:
        return render(request, 'error.html', {'topic': topic_obj.id, 'topic_obj': topic_obj, 'tests': tests})


class HistoryTopicView(LoginRequiredMixin, View):
    def get(self, request, topic):
        user = request.user
        topic_obj = Topic.objects.filter(id=topic).first()
        qs = TestMark.objects.filter(user=user).filter(topic=topic_obj).order_by('quiz', '-date')
        quiz_id_dict = {}
        quiz_qs = Quiz.objects.filter(topic=topic)
        for quiz in quiz_qs:
            quiz_id_dict[quiz.name] = quiz.id
        return render(request, 'history.html', {'topic': topic, 'topic_obj': topic_obj, 'attempts': qs, 'quiz_id_dict': quiz_id_dict})


class HistoryAllTopicView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        qs = TestMark.objects.filter(user=user).order_by('quiz', '-date')
        topic_id_info = {}
        quiz_id_info = {}
        topic_qs = Topic.objects.all()
        quiz_qs = Quiz.objects.all()
        for topic in topic_qs:
            topic_id_info[topic.name] = topic.id
        for quiz in quiz_qs:
            quiz_id_info[quiz.name] = quiz.id
        return render(request, 'history_all.html', {'attempts': qs, 'topic_id_info': topic_id_info, 'quiz_id_info': quiz_id_info})


def search_tests(request):
    if request.method == "POST":
        searched = request.POST['searched']
        search_result = Quiz.objects.filter(name__contains=searched).order_by('topic')
        if search_result.count() == 0:
            search_result = Quiz.objects.all().order_by('topic')
            reply = " тестов не найдено: приводим полный список тестов"
        else:
            reply = " найдено тестов: " + str(search_result.count())
        return render(request, 'search_tests.html', {'searched': searched, 'search_result': search_result, 'reply': reply})
    else:
        return render(request, 'search_error.html', {})
