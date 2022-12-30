from django.urls import path, include
from .views import StartView, TestsView, StartTestView, ResultTestView
urlpatterns = [
    path('topics/', StartView.as_view(), name='all_topics'),
    path('topics/<int:topic>/', TestsView.as_view(), name='tests'),
    path('topics/<int:topic>/test/<int:test>/', StartTestView.as_view(), name='start_test'),
    path('topics/<int:topic>/test/<int:test>/res/', ResultTestView.as_view(), name='test_res')
]