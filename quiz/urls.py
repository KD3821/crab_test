from django.urls import path, include
from .views import StartView

urlpatterns = [
    path('topics/', StartView.as_view(), name='all_topics'),
    # path('<topic:pk>/start', ),
    # path('<topic:pk>/<question:pk>', ),
    # path('<topic:pk>/result', )
]