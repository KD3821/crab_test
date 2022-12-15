from django.shortcuts import render
from django.views import View
from .models import *

class StartView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        topics = Topic.objects.all()
        return render(request, 'start.html', {'topics': topics, 'user': user})
