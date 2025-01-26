from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.db.models import Count 
from datetime import date, datetime

from django.urls import reverse
from .forms import CustomUserForm, ParticipanteForm, EventoForm, ProfessorForm, AtividadeForm, AddParticipanteEventoForm, AddAlunoEventoForm, AddProfessorEventoForm, AlunoForm, AvaliacaoForm
from .models import *
from .certificate import generateCertificado

def index(request):
    context = {}
    context['current_date'] = date.today()
    context['atividade'] = atividade = Atividade.objects.get_home_event()
    context["eventos"] = Evento.objects.filter(atividade=atividade).order_by("topico")

    if request.user.is_authenticated:   
        context['user_is_participante'] = Participante.objects.filter(user=request.user).exists()
        context['user_is_inscrito'] = Inscricao.objects.filter(atividade=atividade, participante__user=request.user).exists()
    else:
        context['user_is_participante'] = False
        context['user_is_inscrito'] = False

    return render(request, "home.html",context)

@login_required(login_url="/login")
def inscrever(request, event_id):
    atividade = get_object_or_404(Atividade, pk=event_id)
    participante = Participante.objects.filter(user=request.user).first()
    
    context = {}
    context['user_is_participante'] = Participante.objects.filter(user=request.user).exists()
    context['user_is_inscrito'] = Inscricao.objects.filter(atividade=atividade, participante__user=request.user).exists()

    if not context['user_is_inscrito'] and context['user_is_participante']:
        inscricao = Inscricao.objects.create(atividade=atividade, participante=participante, confirmado=True,dataHora=datetime.now())
        inscricao.save()
        
    return redirect("home")

@login_required(login_url="/login")
def desinscrever(request, event_id):
    atividade = get_object_or_404(Atividade, pk=event_id)
    participante = Participante.objects.filter(user=request.user).first()
    
    context = {}
    context['user_is_participante'] = Participante.objects.filter(user=request.user).exists()
    context['user_is_inscrito'] = Inscricao.objects.filter(atividade=atividade, participante__user=request.user).exists()

    if context['user_is_inscrito'] and context['user_is_participante']:
        Inscricao.objects.filter(atividade=atividade, participante=participante).delete()

    return redirect("home")

def entrar(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('adminAtividade')
        else:
            return redirect('home')
    
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password'],)
            if user is not None:
                login(request, user)
                #messages.success(request, f"Olá, <b>{user.first_name}</b>! Você logou com sucesso!")
                print("LOGGED IN")
                if user.is_staff:
                    return redirect('adminAtividade')
                else:
                    return redirect('home')
        else:
            for error in list(form.errors.values()):
                print(request, error) 
    
    form = AuthenticationForm()

    return render(request, 'login_user.html', context={'form':form})

def registrarUsuario(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = CustomUserForm(request.POST)
    form2 = ParticipanteForm(request.POST)
    if request.method == "POST":
        if form.is_valid() and form2.is_valid():
            user = form.save(commit=False)
            participante = form2.save(commit=False)

            user.first_name = form2.cleaned_data['nome']
            user.last_name = form2.cleaned_data['sobrenome']
            
            user.save()
            
            participante.user = user
            participante.save()
            #messages.success(request, f"Cadastro realizado com sucesso, <b>{user.first_name}</b>!")
            return redirect('home')
    else:
        form = CustomUserForm(request.POST)
        form2 = ParticipanteForm(request.POST)

    return render(request, 'registro.html', {'form': form, "form2":form2})

@login_required(login_url='login')
def sair(request):
    logout(request)
    #messages.info(request,"Deslogado com sucesso!")
    return redirect('home')

@login_required(login_url="login")
def adminAtividade(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    context = {}
    atividades = Atividade.objects.filter(ativo=True).order_by('data')
    context['atividades'] = atividades
    if 'filter' in request.GET:
        context['atividades'] = Atividade.objects.get_filtered_atividade(request.GET['filter'])
        return render(request, 'admin_atividade.html', context)
    
    if 'pk_atividade' in request.POST:
        print(Atividade.objects.filter(pk=request.POST['pk_atividade']))
        atividade = Atividade.objects.filter(pk=request.POST['pk_atividade']).first()
        atividade.ativo = False
        atividade.save()
        return redirect('adminAtividade')

    return render(request, 'admin_atividade.html', context)

@login_required(login_url='login')
def adminCadastrarAtividade(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    context = {}
    form = AtividadeForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            atividade = form.save()
            #messages.success(request, f"Atividade Cadastrada com sucesso!")
            return redirect('adminAtividade')
        else:
            for error in list(form.errors.values()):
                pass
            context['form'] = AtividadeForm(request.POST)
    else:
        context['form'] = AtividadeForm(initial=AtividadeForm.get_inital_data())    

    return render(request, 'admin_atividade_cadastrar.html', context)

@login_required(login_url='login')
def adminEditarAtividade(request, pk):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    atividade = get_object_or_404(Atividade,pk=pk)
    form = AtividadeForm(request.POST, instance=atividade)
    if request.method == "POST":
        if form.is_valid():
            atividade = form.save()
            #messages.success(request, f"Atividade Cadastrada com sucesso!")
            return redirect('adminAtividade')
        else:
            for error in list(form.errors.values()):
                pass

    context['form'] = AtividadeForm(instance=atividade)    

    return render(request, 'admin_atividade_editar.html', context)


@login_required(login_url="login")
def adminProfessores(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    professores = Professor.objects.all().order_by('id')
    context['professores'] = professores
    if 'filter' in request.GET:
        context['professores'] = Professor.objects.get_filtered_professor(request.GET['filter'])
        return render(request, 'admin_professores.html', context)
    
    if 'pk_professor' in request.POST:
        professor = Professor.objects.filter(pk=request.POST['pk_professor']).first()
        professor.user.delete()
        professor.delete()
        return redirect('adminProfessores')
    
    if 'validar' in request.POST:
        professor = Professor.objects.filter(pk=request.POST['validar']).first()
        professor.user.validated = True
        professor.user.is_staff = True
        professor.user.save()
        return redirect('adminProfessores')

    
    return render(request, 'admin_professores.html', context)

@login_required(login_url='login')
def adminCadastrarProfessores(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    context = {}
    form = CustomUserForm(request.POST)
    form2 = ProfessorForm(request.POST)
    if request.method == "POST":
        if form.is_valid() and form2.is_valid():
            user = form.save(commit=False)
            participante = form2.save(commit=False)

            user.first_name = form2.cleaned_data['nome']
            user.last_name = form2.cleaned_data['sobrenome']
            user.validated = True
            user.is_staff = True
            
            user.save()
            
            participante.user = user
            participante.save()
            #messages.success(request, f"Cadastro realizado com sucesso, <b>{user.first_name}</b>!")
            return redirect('adminProfessores')
    else:
        form = CustomUserForm()
        form2 = ProfessorForm()
    
    context = {"form": form, "form2":form2}
    return render(request, 'admin_professores_cadastrar.html', context)

@login_required(login_url='login')
def adminEditarProfessores(request, pk):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    professor = get_object_or_404(Professor,pk=pk)
    form = CustomUserForm(request.POST, instance=professor.user)
    form2 = ProfessorForm(request.POST, instance=professor)
    if request.method == "POST":
        if form2.is_valid() and form.is_valid():
            professor = form2.save()
            user = form.save()
            #messages.success(request, f"Evento Cadastrado com sucesso!")
            return redirect('adminProfessores')
        else:
            for error in list(form2.errors.values()):
                pass

    context['form2'] = ProfessorForm(instance=professor)    
    context['form'] = CustomUserForm(instance=professor.user)

    return render(request, 'admin_professores_editar.html', context)

def registrarProfessor(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = CustomUserForm(request.POST)
    form2 = ProfessorForm(request.POST)
    if request.method == "POST":
        if form.is_valid() and form2.is_valid():
            user = form.save(commit=False)
            participante = form2.save(commit=False)

            user.first_name = form2.cleaned_data['nome']
            user.last_name = form2.cleaned_data['sobrenome']
            user.validated = False
            user.is_staff = True
            user.save()
            
            participante.user = user
            participante.save()
            #messages.success(request, f"Cadastro realizado com sucesso, <b>{user.first_name}</b>!")
            return redirect('home')
    else:
        form = CustomUserForm(request.POST)
        form2 = ProfessorForm(request.POST)

    return render(request, 'registro_professor.html', {'form': form, "form2":form2})

@login_required(login_url="/login")
def adminCheckin(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    context = {}
    context["atividade"] = atividade = Atividade.objects.get_home_event()
    context["current_date"] = date.today()
    context["inscricoes"] = Inscricao.objects.filter(atividade = atividade).annotate(has_checkin=Count('checkin')).order_by("id")
    
    if 'filter' in request.GET:
        context['inscricoes'] = Inscricao.objects.get_filtered_inscricao(request.GET['filter'], atividade)
        return render(request, "admin_checkin.html", context)
    
    return render(request, "admin_checkin.html", context)

@login_required(login_url="/login")
def adminCheckinValidar(request,pk_atividade, pk_inscricao):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    atividade = Atividade.objects.get(pk=pk_atividade)
    inscricao = get_object_or_404(Inscricao, pk=pk_inscricao, atividade=atividade)
    if not CheckIn.objects.filter(inscricao=inscricao).exists():
        checkin = CheckIn.objects.create(inscricao=inscricao, dataHora=datetime.now())
        checkin.save()

    return redirect('adminCheckin')

@login_required(login_url="/login")
def adminCheckinInvalidar(request, pk_atividade, pk_inscricao):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    atividade = Atividade.objects.get(pk=pk_atividade)
    inscricao = get_object_or_404(Inscricao, pk=pk_inscricao, atividade=atividade)
    checkin = CheckIn.objects.filter(inscricao=inscricao).first()

    if checkin:
        checkin.delete()

    return redirect('adminCheckin')

@login_required(login_url="/login")    
def adminEvento(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    professor = Professor.objects.filter(user = request.user).first()
    context = {}
    context["atividades"] = atividades = Evento.objects.filter(ativo=1)
    context["eventos"] = Evento.objects.filter(professores__in=[professor])

    if 'filter' in request.GET:
        if request.GET['event'] == "-1":
            if request.GET['filter_by'] == "id":
                context["eventos"] = Evento.objects.filter(professores__in=[professor], topico__icontains=request.GET["filter"])
            elif request.GET["filter_by"] == "all":
                context["eventos"] = Evento.objects.filter(topico__icontains=request.GET["filter"])
            else:
                return redirect(adminEvento)
        else:
            if request.GET['filter_by'] == "id":
                context["eventos"] = Evento.objects.filter(evento__pk=request.GET['event'], professores__in=[professor], topico__icontains=request.GET["filter"])
            elif request.GET["filter_by"] == "all":
                context["eventos"] = Evento.objects.filter(evento__pk=request.GET['event'], topico__icontains=request.GET["filter"])
            else:
                return redirect(adminEvento)
        return render(request, "admin_Evento.html", context)

    if 'pk_evento' in request.POST:
        evento = Evento.objects.filter(pk=request.POST['pk_evento']).first()
        evento.delete()
        return redirect(adminEvento)

    return render(request, "admin_evento.html", context)

@login_required(login_url="/login")    
def adminCadastrarEvento(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    context = {}
    form = EventoForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            evento = form.save()
            professor = Professor.objects.get(user = request.user)
            evento.professores.add(professor)
            evento.save()
            #messages.success(request, f"Evento Cadastrado com sucesso!")
            return redirect('adminEvento')
        else:
            for error in list(form.errors.values()):
                pass
            context['form'] = EventoForm(request.POST)
    else:
        context['form'] = EventoForm()
    return render(request, "admin_cadastrar_evento.html", context)

@login_required(login_url="/login")
def adminVisualizarEvento(request,pk):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    context["evento"] = evento = Evento.objects.get(pk=pk)
    professor = Professor.objects.filter(user = request.user).first()
    form = AddParticipanteEventoForm(request.POST)
    form2 = AddAlunoEventoForm(request.POST)
    form3 = AddProfessorEventoForm(request.POST)

    if "pk_participante_remover" in request.POST:
        participante = Participante.objects.get(pk=request.POST["pk_participante_remover"])
        evento.participantes.remove(participante)

    if "pk_aluno_remover" in request.POST:
        aluno = Aluno.objects.get(pk=request.POST["pk_aluno_remover"])
        evento.alunos.remove(aluno)

    if "pk_professor_remover" in request.POST:
        professor = Professor.objects.get(pk=request.POST["pk_professor_remover"])
        evento.professores.remove(professor)

    
    if request.method == 'POST':
        if form.is_valid():
            participante = form.cleaned_data['participante']
            evento.participantes.add(participante)

            return redirect("adminVisualizarEvento", pk=pk)

        if form2.is_valid():
            aluno = form2.cleaned_data['aluno']
            evento.alunos.add(aluno)

            return redirect("adminVisualizarEvento", pk=pk)
        
        if form3.is_valid():
            professor = form3.cleaned_data['professor']
            evento.professores.add(professor)

            return redirect("adminVisualizarEvento", pk=pk)
    else:
        form = AddParticipanteEventoForm()
        form2 = AddAlunoEventoForm()
        form3 = AddProfessorEventoForm()
    
    context["form"] = form
    context["form2"] = form2
    context["form3"] = form3
    context["size"] = evento.professores.count()
    context["in_evento"] = Evento.objects.filter(pk=pk,professores__in=[professor]).exists()
    return render(request, "admin_evento_visualizar.html", context)

@login_required(login_url='login')
def adminEditarEvento(request, pk):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    evento = get_object_or_404(Evento,pk=pk)
    form = EventoForm(request.POST, instance=evento)
    
    if request.method == "POST":
        if form.is_valid():
            evento = form.save()
            #messages.success(request, f"Evento Cadastrado com sucesso!")
            return redirect('adminEvento')
        else:
            for error in list(form.errors.values()):
                pass

    context['form'] = EventoForm(instance=evento)

    return render(request, 'admin_evento_editar.html', context)


@login_required(login_url="/login")
def adminParticipante(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    participante = Participante.objects.all().order_by('id')
    context['participantes'] = participante
    if 'filter' in request.GET:
        context['participantes'] = Participante.objects.get_filtered_participante(request.GET['filter'])
        return render(request, 'admin_participante.html', context)
    
    if 'pk_participante' in request.POST:
        participante = Participante.objects.filter(pk=request.POST['pk_participante']).first()
        participante.user.delete()
        participante.delete()
        return redirect('adminParticipante')
    
    return render(request, 'admin_participante.html', context)

@login_required(login_url='login')
def adminCadastrarParticipante(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    context = {}
    form = CustomUserForm(request.POST)
    form2 = ParticipanteForm(request.POST)
    if request.method == "POST":
        if form.is_valid() and form2.is_valid():
            user = form.save(commit=False)
            participante = form2.save(commit=False)

            user.first_name = form2.cleaned_data['nome']
            user.last_name = form2.cleaned_data['sobrenome']
            user.validated = False
            user.is_staff = False
            
            user.save()
            
            participante.user = user
            participante.save()
            #messages.success(request, f"Cadastro realizado com sucesso, <b>{user.first_name}</b>!")
            return redirect('adminParticipante')
    else:
        form = CustomUserForm()
        form2 = ParticipanteForm()
    
    context = {"form": form, "form2":form2}
    return render(request, 'admin_participante_cadastrar.html', context)

@login_required(login_url='login')
def adminEditarParticipante(request, pk):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    participante = get_object_or_404(Participante,pk=pk)
    form = CustomUserForm(request.POST, instance=participante.user)
    form2 = ParticipanteForm(request.POST, instance=participante)
    if request.method == "POST":
        if form2.is_valid() and form.is_valid():
            participante = form2.save()
            user = form.save()
            #messages.success(request, f"Evento Cadastrado com sucesso!")
            return redirect('adminParticipante')
        else:
            for error in list(form2.errors.values()):
                pass

    context['form2'] = ParticipanteForm(instance=participante)    
    context['form'] = CustomUserForm(instance=participante.user)

    return render(request, 'admin_participante_editar.html', context)

@login_required(login_url="/login")
def adminAluno(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    aluno = Aluno.objects.all().order_by('id')
    context['alunos'] = aluno
    
    if 'filter' in request.GET:
        context['alunos'] = Aluno.objects.get_filtered_aluno(request.GET['filter'])
        return render(request, 'admin_aluno.html', context)
    
    if 'pk_aluno' in request.POST:
        aluno = Aluno.objects.filter(pk=request.POST['pk_aluno']).first()
        aluno.delete()
        return redirect('adminAluno')
    
    return render(request, 'admin_aluno.html', context)

@login_required(login_url='/login')
def adminCadastrarAluno(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    form = AlunoForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            #messages.success(request, f"Cadastro realizado com sucesso, <b>{user.first_name}</b>!")
            return redirect('adminAluno')
    else:
        form = AlunoForm()
    
    context = {"form": form}
    return render(request, 'admin_aluno_cadastrar.html', context)

@login_required(login_url='login')
def adminEditarAluno(request, pk):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    aluno = get_object_or_404(Aluno,pk=pk)
    form = AlunoForm(request.POST, instance=aluno)
    if request.method == "POST":
        if form.is_valid():
            aluno = form.save()
            #messages.success(request, f"Evento Cadastrado com sucesso!")
            return redirect('adminAluno')
        else:
            for error in list(form.errors.values()):
                pass

    context['form'] = AlunoForm(instance=aluno)

    return render(request, 'admin_aluno_editar.html', context)


@login_required(login_url="/login")
def adminAvaliar(request, pk_Evento, pk_aluno):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    context["aluno"]= aluno = get_object_or_404(Aluno,pk=pk_aluno)
    context["Evento"] = Evento = get_object_or_404(Evento,pk=pk_Evento)
    avaliacao = Avaliacao.objects.filter(aluno=aluno, Evento=Evento)
    context['avaliacoes'] = avaliacao
    
    if 'filter' in request.GET:
        if request.GET["filter"] == "":
            return render(request, 'admin_avaliar_aluno.html', context)

        context['avaliacoes'] = Avaliacao.objects.filter(aluno=aluno, Evento=Evento, dataAvaliacao=request.GET['filter'])
        return render(request, 'admin_avaliar_aluno.html', context)
    
    if 'pk_avaliacao' in request.POST:
        avaliacao = Avaliacao.objects.filter(pk=request.POST['pk_avaliacao']).first()
        avaliacao.delete()
        return redirect('adminAvaliar', pk_Evento=pk_Evento, pk_aluno=pk_aluno)
    
    return render(request, 'admin_avaliar_aluno.html', context)

@login_required(login_url='/login')
def adminCadastrarAvaliacao(request, pk_aluno, pk_Evento):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    form = AvaliacaoForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            user = get_object_or_404(Aluno,pk=pk_aluno)
            Evento = get_object_or_404(Evento,pk=pk_Evento)
            avaliacao = form.save(commit=False)
            avaliacao.dataAvaliacao = date.today()
            avaliacao.aluno = user
            avaliacao.Evento = Evento
            avaliacao.save()

            #messages.success(request, f"Cadastro realizado com sucesso, <b>{user.first_name}</b>!")
            return redirect('adminAvaliar', pk_aluno, pk_Evento)
    else:
        form = AvaliacaoForm()
    
    context = {"form": form}
    return render(request, 'admin_avaliar_aluno_cadastrar.html', context)

@login_required(login_url='login')
def adminEditarAvaliacao(request, pk):
    if not request.user.validated:
        logout(request)
        return redirect('home')
    
    context = {}
    avaliacao = get_object_or_404(Avaliacao,pk=pk)
    form = AvaliacaoForm(request.POST, instance=avaliacao)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            #messages.success(request, f"Evento Cadastrado com sucesso!")
            return redirect('adminAvaliar', pk_Evento = avaliacao.Evento.id, pk_aluno = avaliacao.aluno.id)
        else:
            for error in list(form.errors.values()):
                pass

    context['form'] = AvaliacaoForm(instance=avaliacao)
    return render(request, 'admin_avaliar_aluno_editar.html', context)

@login_required(login_url="/login")
def adminCertificado(request):
    if not request.user.validated:
        logout(request)
        return redirect('home')

    context = {}
    # Obtendo o evento atual
    context["atividade"] = atividade = Atividade.objects.get_last_event()

    # Lista de participantes, considerando check-ins
    participantes_com_checkin = Participante.objects.filter(evento__atividade=atividade).distinct()

    # Filtrando para incluir apenas os participantes com check-in
    participantes_com_checkin = [
        participante for participante in participantes_com_checkin
        if CheckIn.objects.filter(inscricao__participante=participante).exists()
    ]
    
    context["participantes"] = participantes_com_checkin
    context["alunos"] = Aluno.objects.filter(evento__atividade=atividade).distinct()
    context["professores"] = Professor.objects.filter(evento__atividade=atividade).distinct()
    context["atividades"] = Atividade.objects.filter(ativo=1, data__lte=date.today())

    # Filtro baseado em parâmetros da URL
    if 'filter' in request.GET:
        if request.GET['event'] == "-1":
            context["participantes"] = Participante.objects.get_filtered_participante(request.GET['filter']).filter(evento__atividade=atividade)
            context["alunos"] = Aluno.objects.get_filtered_aluno(request.GET['filter']).filter(evento__atividade=atividade)
            context["professores"] = Professor.objects.get_filtered_professor(request.GET['filter']).filter(evento__atividade=atividade)
        else:
            context["participantes"] = Participante.objects.get_filtered_participante(request.GET['filter']).filter(evento__atividade=request.GET['event'])
            context["alunos"] = Aluno.objects.get_filtered_aluno(request.GET['filter']).filter(evento__atividade=request.GET['event'])
            context["professores"] = Professor.objects.get_filtered_professor(request.GET['filter']).filter(evento__atividade=request.GET['event'])

        return render(request, "admin_certificados.html", context)

    return render(request, "admin_certificados.html", context)


@login_required(login_url="/login")
def adminDownloadCertificado(request, pk_evento, pk_participante):

    evento = get_object_or_404(Evento, pk=pk_evento)
    usuario = get_object_or_404(Usuario, pk=pk_participante)
    certificado = Certificado.objects.filter(evento=evento, usuario=usuario)

    if(Evento.objects.filter(alunos=usuario, evento=evento).exists()):
        Evento = Evento.objects.filter(alunos=usuario, evento=evento).first()
    elif(Evento.objects.filter(professores=usuario, evento=evento).exists()):
        Evento = Evento.objects.filter(professores=usuario, evento=evento).first()
    else:
        redirect("adminCertificado")

    if certificado:
        pdf_path = certificado.first().codigo
    else:
        date_time = evento.data.strftime("%d/%m/%Y")
        diff = evento.data - Evento.data_cadastro
        semana = (diff.days // 7) * 14
        pdf_path = generateCertificado(usuario.nome+" "+usuario.sobrenome, evento.tema, date_time, str(semana))
        certificado = Certificado(dataEmissao=datetime.now(), codigo=pdf_path, evento=evento, usuario=usuario)
        certificado.save()

    with open(pdf_path, "rb") as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="certificado.pdf"'
    return response

@login_required(login_url="/login")
def certificados(request):
    context = {}
    context["participante"] = participante = Participante.objects.get(user=request.user.id)
    context["atividades"] = evento = Evento.objects.filter(inscricao__participante=participante, inscricao__checkin__isnull=False, data__lt=date.today()).distinct()
    print(evento)
    

    return render(request, "certificados.html", context)

@login_required(login_url="/login")
def downloadCertificado(request, pk_evento, pk_participante):
    evento = get_object_or_404(Evento, pk=pk_evento)
    participante = get_object_or_404(Participante, user=pk_participante)
    certificado = Certificado.objects.filter(evento=evento, usuario=participante)
    inscricao = Inscricao.objects.filter(evento = evento, participante = participante).first()
    check = CheckIn.objects.filter( inscricao = inscricao).first()

    if certificado:
        pdf_path = certificado.first().codigo
    else:
        if check:
            date_time = evento.data.strftime("%d/%m/%Y")
            pdf_path = generateCertificado(participante.nome+" "+participante.sobrenome, evento.tema, date_time, str(evento.duracaoEvento()))
            certificado = Certificado(dataEmissao=datetime.now(), codigo=pdf_path, evento=evento, usuario=participante)
            certificado.save()
        else:
            return redirect("certificados")
        
    with open(pdf_path, "rb") as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="certificado.pdf"'
    return response

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        item.delete()
        #messages.success(request, "Item excluído com sucesso!")
        return redirect('lista_de_itens')

    # Redireciona se acessar via GET (opcional)
    #messages.error(request, "Ação inválida.")
    return redirect('lista_de_itens')