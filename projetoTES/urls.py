"""
URL configuration for projetoTES project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import path
from projetoApp import views
from django.conf.urls.static import static
from projetoApp.views import deleteItem

urlpatterns = [
    path('admin_evento/', views.adminEvento, name = "adminEvento"),
    path('admin_evento/cadastrar/', views.adminCadastrarEvento, name = "adminCadastrarEvento"),
    path('admin_evento/<int:pk>/', views.adminEditarEvento, name = "adminEditarEvento"),
    path('admin_evento/desativar/<int:pk>/', views.adminDesativarEvento, name='adminDesativarEvento'),
    path('admin_evento/reativar/<int:pk>/', views.adminReativarEvento, name='adminReativarEvento'),
    path('admin_professores/', views.adminProfessores, name = "adminProfessores"),
    path('admin_professores/cadastrar/', views.adminCadastrarProfessores, name = "adminCadastrarProfessores"),
    path('admin_professores/<int:pk>/', views.adminEditarProfessores, name = "adminEditarProfessores"),
    path('admin_checkin/', views.adminCheckin, name = "adminCheckin"),
    path('admin_checkin/validar_participante/<int:pk_evento>/<int:pk_inscricao>', views.adminCheckinValidarParticipante, name = "adminCheckinValidarParticipante"),
    path('admin_checkin/invalidar_participante/<int:pk_evento>/<int:pk_inscricao>', views.adminCheckinInvalidarParticipante, name = "adminCheckinInvalidarParticipante"),
    path('admin_checkin/validar_aluno/<int:pk_evento>/<int:pk_aluno>/<int:pk_atividade>', views.adminCheckinValidarAluno, name = "adminCheckinValidarAluno"),
    path('admin_checkin/invalidar_aluno/<int:pk_evento>/<int:pk_aluno>/<int:pk_atividade>', views.adminCheckinInvalidarAluno, name = "adminCheckinInvalidarAluno"),
    path('admin_atividade/', views.adminAtividade, name = "adminAtividade"),
    path('admin_atividade/cadastrar', views.adminCadastrarAtividade, name = "adminCadastrarAtividade"),
    path('admin_atividade/<int:pk>/', views.adminEditarAtividade, name = "adminEditarAtividade"),
    path('admin_atividade_visualizar/<int:pk>/', views.adminVisualizarAtividade, name = "adminVisualizarAtividade"),
    path('admin_avaliar/<int:pk_aluno>/<int:pk_atividade>', views.adminAvaliar, name = "adminAvaliar"),
    path('admin_avaliar/cadastrar/<int:pk_aluno>/<int:pk_atividade>', views.adminCadastrarAvaliacao, name = "adminCadastrarAvaliacao"),
    path('admin_avaliar/<int:pk>', views.adminEditarAvaliacao, name = "adminEditarAvaliacao"),
    path('admin_participante/', views.adminParticipante, name = "adminParticipante"),
    path('admin_participante/cadastrar', views.adminCadastrarParticipante, name = "adminCadastrarParticipante"),
    path('admin_participante/<int:pk>', views.adminEditarParticipante, name = "adminEditarParticipante"),
    path('admin_aluno/', views.adminAluno, name = "adminAluno"),
    path('admin_aluno/cadastrar', views.adminCadastrarAluno, name = "adminCadastrarAluno"),
    path('admin_aluno/<int:pk>', views.adminEditarAluno, name = "adminEditarAluno"),
    path('admin_instituicao/', views.adminInstituicao, name='adminInstituicao'),
    path('admin_instituicao/cadastrar/', views.adminCadastrarInstituicao, name='adminCadastrarInstituicao'),
    path('admin_instituicao/editar/<int:pk>/', views.adminEditarInstituicao, name='adminEditarInstituicao'),
    path('admin_instituicao_visualizar/<int:pk>/', views.adminVisualizarInstituicao, name='adminVisualizarInstituicao'),
    path('admin_certificados/', views.adminCertificado, name = "adminCertificado"),
    path('certificados/', views.certificados, name = "certificados"),
    path("", views.index, name = 'home'),
    path("login/", views.entrar, name = 'login'),
    path("registrar/", views.registrarUsuario, name = 'registrarUsuario'),
    path("registrar_professor/", views.registrarProfessor, name = 'registrarProfessor'),
    path("logout/", views.sair, name = 'logout'),
    path('inscrever/<int:event_id>/', views.inscrever, name='inscrever'),
    path('desinscrever/<int:event_id>/', views.desinscrever, name='desinscrever'),
    path('admin_download_certificado/<int:pk_evento>/<int:pk_participante>/', views.adminDownloadCertificado, name='adminDownloadCertificado'),
    path('download_certificado/<int:pk_evento>/<int:pk_participante>/', views.downloadCertificado, name='downloadCertificado'),
    path('delete/<str:model>/<int:id>/', deleteItem, name='deleteItem'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)