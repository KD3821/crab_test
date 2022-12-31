from django.urls import path, include
from .views import StartView, TestsView, StartTestView, ResultTestView, HistoryTopicView, HistoryAllTopicView, del_q_marks
urlpatterns = [
    path('topics/', StartView.as_view(), name='all_topics'),
    path('topics/<int:topic>/', TestsView.as_view(), name='tests'),
    path('topics/<int:topic>/test/<int:test>/', StartTestView.as_view(), name='start_test'),
    path('topics/<int:topic>/test/<int:test>/res/', ResultTestView.as_view(), name='test_res'),
    path('topics/<int:topic>/test/<int:test>/again/', del_q_marks, name='reset_start_test'),
    path('topics/<int:topic>/hist/', HistoryTopicView.as_view(), name='history_tests'),
    path('topics/allhist/', HistoryAllTopicView.as_view(), name='history_topics'),

]