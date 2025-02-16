from abc import ABC, abstractmethod
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import logout
from .models import CheckIn, Inscricao, Aluno, Atividade, Evento

class CheckInHandler(ABC):
    def __init__(self, request, evento_id, entity_id):
        """
        :param request: HttpRequest
        :param evento_id: ID do evento (ou atividade)
        :param entity_id: Para participante, é o ID da inscrição; para aluno, é o ID do aluno.
        """
        self.request = request
        self.evento_id = evento_id
        self.entity_id = entity_id

    def _check_authentication(self):
        """Verifica se o usuário está autenticado e validado."""
        if not self.request.user.validated:
            logout(self.request)
            return redirect('home')
        return True

    @abstractmethod
    def entity_type(self):
        """Retorna o tipo de entidade: 'aluno' ou 'participante'."""
        pass

    @abstractmethod
    def _get_object(self):
        """Obtém o objeto relacionado ao check-in (por exemplo, Inscricao ou (Aluno, Atividade))."""
        pass

    @abstractmethod
    def _create_checkin_params(self):
        """Cria os parâmetros para o check-in."""
        pass

    def validar(self):
        """Valida o check-in, criando o registro correspondente."""
        auth_result = self._check_authentication()
        if auth_result is not True:
            return auth_result

        params = self._create_checkin_params()

        # Se a entidade for 'aluno' e _create_checkin_params retornar uma lista (caso o aluno esteja em múltiplas atividades),
        # itere sobre ela; caso contrário, crie um único check-in.
        if self.entity_type() == 'aluno':
            if isinstance(params, list):
                for p in params:
                    CheckIn.objects.create(**p)
            else:
                CheckIn.objects.create(**params)
        else:  # Para participantes
            CheckIn.objects.create(**params)
        return redirect('adminCheckin')

    def invalidar(self):
        """Invalida o check-in, removendo o registro correspondente."""
        auth_result = self._check_authentication()
        if auth_result is not True:
            return auth_result

        params = self._create_checkin_params()
        CheckIn.objects.filter(**params).delete()
        return redirect('adminCheckin')


# Subclasse para check-in de participantes (inscrição)
class ParticipanteCheckInHandler(CheckInHandler):
    def entity_type(self):
        return 'participante'

    def _get_object(self):
        """Obtém a inscrição do participante."""
        return get_object_or_404(Inscricao, id=self.entity_id, evento_id=self.evento_id)

    def _create_checkin_params(self):
        inscricao = self._get_object()
        return {
            'dataHora': timezone.now(),
            'inscricao': inscricao
        }
    
    def invalidar(self):
        """Invalida o check-in do participante removendo-o com base no evento e na inscrição."""
        auth_result = self._check_authentication()
        if auth_result is not True:
            return auth_result

        evento = get_object_or_404(Evento, id=self.evento_id)
        inscricao = get_object_or_404(Inscricao, id=self.entity_id, evento=evento)

        checkin = CheckIn.objects.filter(inscricao=inscricao).first()
        if checkin:
            checkin.delete()

        return redirect('adminCheckin')


# Subclasse para check-in de alunos vinculados a atividades
class AlunoCheckInHandler(CheckInHandler):
    def __init__(self, request, evento_id, entity_id, pk_atividade):
        super().__init__(request, evento_id, entity_id)
        self.pk_atividade = pk_atividade  # Adiciona o ID da atividade

    def entity_type(self):
        return 'aluno'

    def _get_object(self):
        """Obtém o aluno e a atividade relacionada.
           Aqui, 'entity_id' é o ID do aluno, e 'pk_atividade' é o ID da atividade.
        """
        aluno = get_object_or_404(Aluno, id=self.entity_id)
        atividade = get_object_or_404(Atividade, id=self.pk_atividade, evento_id=self.evento_id, alunos=aluno)
        return aluno, atividade

    def _create_checkin_params(self):
        aluno, atividade = self._get_object()
        return {
            'dataHora': timezone.now(),
            'aluno': aluno,
            'atividade': atividade
        }

    def invalidar(self):
        """Invalida o check-in do aluno removendo-o com base no aluno e na atividade."""
        auth_result = self._check_authentication()
        if auth_result is not True:
            return auth_result

        aluno, atividade = self._get_object()
        CheckIn.objects.filter(aluno=aluno, atividade=atividade).delete()
        return redirect('adminCheckin')


def get_checkin_handler(model_type, request, evento_id, entity_id, pk_atividade=None):
    model_type = model_type.lower()
    if model_type == 'participante':
        return ParticipanteCheckInHandler(request, evento_id, entity_id)
    elif model_type == 'aluno':
        return AlunoCheckInHandler(request, evento_id, entity_id, pk_atividade)
    else:
        raise ValueError("Tipo de entidade não suportado para check-in.")