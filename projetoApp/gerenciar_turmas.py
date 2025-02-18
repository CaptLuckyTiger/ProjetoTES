from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import path
from django.views import View

from projetoApp.models import Professor


class Turma(models.Model):
    nome_turma = models.CharField(max_length=100)
    numero_sala = models.IntegerField()
    periodo = models.CharField(max_length=50)
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, blank=True)  # Relacionamento com Professor
    email_responsavel = models.EmailField()
    materia = models.CharField(max_length=100)
    quantidade_alunos = models.IntegerField()
    necessidades_especificas = models.TextField(blank=True, null=True)


class TurmaHandler:
    def listar_turmas(self):
        return Turma.objects.all()

    def criar_turma(self, data):
        return Turma.objects.create(**data)

    def editar_turma(self, turma_id, data):
        turma = get_object_or_404(Turma, id=turma_id)
        for key, value in data.items():
            setattr(turma, key, value)
        turma.save()
        return turma

    def deletar_turma(self, turma_id):
        turma = get_object_or_404(Turma, id=turma_id)
        turma.delete()


class TurmaListView(View):
    def get(self, request):
        handler = TurmaHandler()
        turmas = handler.listar_turmas()
        return render(request, 'turma_list.html', {'turmas': turmas})



def listar_turmas(request):
    handler = TurmaHandler()
    turmas = handler.listar_turmas()
    return render(request, 'turmas_list.html', {'turmas': turmas})

def criar_turma(request):
    if request.method == 'POST':
        handler = TurmaHandler()
        data = {
            'nome_turma': request.POST['nome_turma'],
            'numero_sala': request.POST['numero_sala'],
            'periodo': request.POST['periodo'],
            'professor': request.POST['professor'],
        }
        handler.criar_turma(data)
        return redirect('listar_turmas')


    def get(self, request):
        return render(request, 'turma_form.html')

    def post(self, request):
        data = {
            'nome_turma': request.POST['nome_turma'],
            'numero_sala': request.POST['numero_sala'],
            'professor_responsavel': request.POST['professor_responsavel'],
            'email_responsavel': request.POST['email_responsavel'],
            'materia': request.POST['materia'],
            'periodo': request.POST['periodo'],
            'quantidade_alunos': request.POST['quantidade_alunos'],
            'necessidades_especificas': request.POST.get('necessidades_especificas', '')
        }
        handler = TurmaHandler()
        handler.criar_turma(data)
        return redirect('turma_list')

class TurmaEditView(View):
    def get(self, request, turma_id):
        turma = get_object_or_404(Turma, id=turma_id)
        return render(request, 'turma_form.html', {'turma': turma})

    def post(self, request, turma_id):
        data = {
            'nome_turma': request.POST['nome_turma'],
            'numero_sala': request.POST['numero_sala'],
            'professor_responsavel': request.POST['professor_responsavel'],
            'email_responsavel': request.POST['email_responsavel'],
            'materia': request.POST['materia'],
            'periodo': request.POST['periodo'],
            'quantidade_alunos': request.POST['quantidade_alunos'],
            'necessidades_especificas': request.POST.get('necessidades_especificas', '')
        }
        handler = TurmaHandler()
        handler.editar_turma(turma_id, data)
        return redirect('turma_list')


urlpatterns = [
    path('turmas/', TurmaListView.as_view(), name='turma_list'),
    path('turmas/editar/<int:turma_id>/', TurmaEditView.as_view(), name='turma_edit'),
]



