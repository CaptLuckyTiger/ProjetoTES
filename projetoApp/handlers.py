from abc import ABC, abstractmethod
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import logout
from .models import CheckIn, Inscricao, Aluno, Atividade

from abc import ABC, abstractmethod
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import logout
from .models import CheckIn, Inscricao, Aluno, Atividade

class CheckInHandler(ABC):
    def __init__(self, request, evento_id, user_id):
        self.request = request
        self.evento_id = evento_id
        self.user_id = user_id

    def _check_authentication(self):
        """Verifica se o usuário está autenticado e validado."""
        if not self.request.user.validated:
            logout(self.request)
            return redirect('home')
        return True  # Retorna True se o usuário estiver autenticado

    @abstractmethod
    def _get_object(self):
        """Obtém o objeto relacionado ao check-in (inscrição ou aluno)."""
        pass

    @abstractmethod
    def _create_checkin_params(self):
        """Cria os parâmetros para o check-in."""
        pass

    def validar(self):
        """Valida o check-in."""
        if not self._check_authentication():
            return redirect('home')  # Redireciona se o usuário não estiver autenticado

        # Obtém os parâmetros do check-in
        checkin_params = self._create_checkin_params()
    
        # Cria o check-in no banco de dados
        CheckIn.objects.create(**checkin_params)
        return redirect('adminCheckin')

    def invalidar(self):
        """Invalida o check-in."""
        if not self._check_authentication():
            return redirect('home')  # Redireciona se o usuário não estiver autenticado
    
        # Obtém os parâmetros do check-in
        checkin_params = self._create_checkin_params()
        
        # Remove o check-in do banco de dados
        CheckIn.objects.filter(**checkin_params).delete()
        return redirect('adminCheckin')

# Subclasses concretas
class ParticipanteCheckInHandler(CheckInHandler):
    def _get_object(self):
        """Obtém a inscrição do participante."""
        return get_object_or_404(Inscricao, id=self.user_id, evento_id=self.evento_id)

    def _create_checkin_params(self): 
        """Cria os parâmetros para o check-in do participante."""
        inscricao = self._get_object()
        return {
            'dataHora': timezone.now(),
            'inscricao': inscricao
        }

class AlunoCheckInHandler(CheckInHandler):
    def _get_object(self):
        """Obtém o aluno e a atividade relacionada."""
        aluno = get_object_or_404(Aluno, id=self.user_id)
        atividade = get_object_or_404(Atividade, evento_id=self.evento_id, alunos=aluno)
        return aluno, atividade

    def _create_checkin_params(self):
        """Cria os parâmetros para o check-in do aluno."""
        aluno, atividade = self._get_object()
        return {
            'dataHora': timezone.now(),
            'aluno': aluno,
            'atividade': atividade
        }
    def invalidar(self):
        """Invalida o check-in do aluno."""
        if not self._check_authentication():
            return redirect('home')

        aluno, atividade = self._get_object()
        CheckIn.objects.filter(aluno=aluno, atividade=atividade).delete()
        return redirect('adminCheckin')