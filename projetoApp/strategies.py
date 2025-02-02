from django.shortcuts import get_object_or_404
from abc import ABC, abstractmethod

class DeleteStrategy(ABC):
    @abstractmethod
    def delete(self, id):
        pass

class AlunoDeleteStrategy(DeleteStrategy):
    def delete(self, id):
        from .models import Aluno
        item = get_object_or_404(Aluno, id=id)
        item.delete()

class ProfessorDeleteStrategy(DeleteStrategy):
    def delete(self, id):
        from .models import Professor
        item = get_object_or_404(Professor, id=id)
        item.delete()

class ParticipanteDeleteStrategy(DeleteStrategy):
    def delete(self, id):
        from .models import Participante
        item = get_object_or_404(Participante, id=id)
        item.delete()

class EventoDeleteStrategy(DeleteStrategy):
    def delete(self, id):
        from .models import Evento
        item = get_object_or_404(Evento, id=id)
        item.delete()

class AtividadeDeleteStrategy(DeleteStrategy):
    def delete(self, id):
        from .models import Atividade
        item = get_object_or_404(Atividade, id=id)
        item.delete()