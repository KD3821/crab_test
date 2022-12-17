from django.urls import path, include
from .views import StartView

urlpatterns = [
    path('topics/', StartView.as_view(), name='all_topics'),
]