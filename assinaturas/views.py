from django.shortcuts import render

from django.shortcuts import render
# Create your views here.


def assinaturas_mentor(request):
    template_name = 'assinatura/assinaturas_mentor.html'
    return render(request, template_name, {})
