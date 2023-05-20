from django.shortcuts import render
from django.views import View
# Create your views here.


class MentoriasView(View):
    template_name = 'mentorias/mentorias_home.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
