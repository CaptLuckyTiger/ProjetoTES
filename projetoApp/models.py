from django.db import models
from django.contrib.auth.models import AbstractUser
from localflavor.br.models import BRCPFField
from .managers import CustomUserManager, EventoManager, ProfessorManager, InscricaoManager, ParticipanteManager, AlunoManager
from datetime import date, datetime
from django.core.exceptions import ValidationError

# Create your models here.
class CustomUser(AbstractUser):
    first_name = models.CharField(max_length = 30, blank = True)
    last_name = models.CharField(max_length = 30, blank = True)
    username = models.CharField(max_length = 30, blank= True, unique=False, default="")
    email = models.EmailField(verbose_name="E-mail",unique=True)
    validated = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

class Usuario(models.Model):
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE, null=True)
    nome = models.CharField(verbose_name = "Nome", max_length = 50, blank = False)
    sobrenome = models.CharField(verbose_name = "Sobrenome", max_length = 50, blank = False)
    cpf = BRCPFField(name="CPF")

    def __str__(self):
        return self.user.email

class Instituicao(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    endereco = models.TextField()

class Participante(models.Model):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    idade = models.IntegerField(null=True, blank=True)  # Campo de idade
    instituicao = models.ForeignKey(Instituicao, on_delete=models.SET_NULL, null=True, blank=True)  # Relacionamento com Instituicao
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Aluno(Usuario):
    objects = AlunoManager()
    def __str__(self):
        return f'{self.nome} {self.sobrenome}'

class Professor(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)



from django.db import models

class Instituicao(models.Model):
    nome = models.CharField(verbose_name="Nome da Instituição", max_length=255, blank=False)
    telefone = models.CharField(verbose_name="Telefone", max_length=15, blank=True, null=True)
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True)
    endereco = models.CharField(verbose_name="Endereço", max_length=255, blank=True, null=True)
    cidade = models.CharField(verbose_name="Cidade", max_length=100, blank=True, null=True)
    estado = models.CharField(verbose_name="Estado", max_length=2, blank=True, null=True)
    participantes = models.ManyToManyField(Participante, verbose_name="Participantes")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Instituição"
        verbose_name_plural = "Instituições"

class Evento(models.Model):
    tema = models.CharField(verbose_name = "Tema", max_length = 255, blank = False, default="Evento")
    descricao = models.TextField(verbose_name = "Descrição", blank = False)
    data = models.DateField(verbose_name = "Data", null = False, default=date.today)
    horario_inicio = models.TimeField(verbose_name = "Horario Inicio", blank = True,default="8:00")
    horario_fim = models.TimeField(verbose_name= "Horario Fim", blank = True, default="18:00")
    logradouro = models.CharField(verbose_name= "Logradouro", max_length=255, blank=False, default="R. Pref. Brásílio Ribas, 775")
    bairro = models.CharField(verbose_name= "Bairro", max_length=255, blank=False, default="São José")
    cidade = models.CharField(verbose_name= "Cidade", max_length=50, blank=False, default="Ponta Grossa")
    estado = models.CharField(verbose_name= "UF", max_length=50, blank=False, default="Paraná")
    banner = models.URLField(verbose_name="Banner", blank = True)
    ativo = models.BooleanField(verbose_name="Ativo", blank=False, null= False, default=True)

    objects = EventoManager()

    def duracaoEvento(self):
        inicio = datetime.combine(date.today(), self.horario_fim)
        fim = datetime.combine(date.today(), self.horario_inicio)
        diff = inicio - fim
        return diff.total_seconds() / 3600

    def __str__(self):
        return self.tema

class Atividade(models.Model):
    topico = models.CharField(verbose_name="Tópico", max_length = 255, null=True, blank=False)
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    participantes = models.ManyToManyField(Participante, verbose_name="Participantes")
    alunos = models.ManyToManyField(Aluno, verbose_name="Alunos")
    professores = models.ManyToManyField(Professor, verbose_name="Professores")
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE,null=True)
    ativo = models.BooleanField(verbose_name="Ativo", blank=False, null= False, default=True)
    data_cadastro = models.DateField(verbose_name="Data Criação", default=date.today)
    horario_inicio = models.TimeField(verbose_name="Horário Início", blank=True, null=True)
    horario_fim = models.TimeField(verbose_name="Horário Fim", blank=True, null=True)
    capacidade_maxima = models.PositiveIntegerField(verbose_name="Capacidade Máxima", default=0, help_text="Número máximo de pessoas na atividade")

    @property
    def vagas_restantes(self):
        total_inscritos = self.participantes.count() + self.alunos.count()
        return self.capacidade_maxima - total_inscritos

    def checar_disponibilidade(self):
        return self.vagas_restantes > 0

    def clean(self):
        super().clean()
        if self.pk:
            total_inscritos = self.participantes.count() + self.alunos.count()
            if self.capacidade_maxima < total_inscritos:
                raise ValidationError(
                    f"A capacidade não pode ser menor que o número atual de inscritos ({total_inscritos})"
                )
            
    def adicionar_participante(self, participante):
        if not self.checar_disponibilidade():
            raise ValidationError("Não há vagas disponíveis nesta atividade")
        self.participantes.add(participante)

    def adicionar_aluno(self, aluno):
        if not self.checar_disponibilidade():
            raise ValidationError("Não há vagas disponíveis nesta atividade")
        self.alunos.add(aluno)

class Avaliacao(models.Model):
    dataAvaliacao = models.DateField(verbose_name="Data Avaliação", null=False)
    descricao = models.TextField(verbose_name="Descrição", blank=False)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, null=False)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, null=False, default=None)

class Inscricao(models.Model):
    dataHora = models.DateTimeField(verbose_name="Horario")
    confirmado = models.BooleanField()
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE, null=False)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=True)

    objects = InscricaoManager()
    
class CheckIn(models.Model):
    dataHora = models.DateTimeField(verbose_name="Horario")
    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE, null=True, blank=True)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, null=True, blank=True, to_field='usuario_ptr_id')
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, null=True, blank=True)


class Certificado(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=False, default=None)
    dataEmissao = models.DateField(verbose_name="Data Emissão", null = False)
    codigo = models.CharField(verbose_name="Código", max_length=255, blank=True)


    