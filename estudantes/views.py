from django.shortcuts import render

from django.shortcuts import render
# Create your views here.


def estudante_login(request):
    template_name = 'estudantes/login_estudante.html'
    return render(request, template_name, {})
