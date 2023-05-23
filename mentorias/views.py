from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.views import View

from .models import Programas
from .forms import CriarProgramasForm
# Create your views here.


class MentoriasView(View):
    template_name = 'mentorias/mentorias_home.html'

    def get(self, request, *args, **kwargs):
        ctx = {
            'mentorias': Programas.objects.filter(mentor=request.user)
        }
        return render(request, self.template_name, ctx)


def criar_programa(request):
    template_name = 'mentorias/criar_programa.html'
    form = CriarProgramasForm()
    if request.method == 'POST':
        form = CriarProgramasForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mentor = request.user
            instance.save()
            return redirect('usuarios:home_mentor')
        else:
            form = CriarProgramasForm(request.POST)
    return render(request, template_name, {'form': form})


def detalhe_mentoria(request, pk):
    ctx = {
        'mentoria': get_object_or_404(Programas, pk=pk)
    }
    return render(request, 'mentorias/mentoria_detalhe.html', ctx)
