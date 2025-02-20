
from django import forms
from .models import CustomUser, Participante, Professor, Aluno, Atividade, Evento, Avaliacao, Instituicao
from django.utils.safestring import mark_safe
from bootstrap_datepicker_plus.widgets import TimePickerInput, DatePickerInput
from django.db.models import Value as V

class CustomUserForm(forms.ModelForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Senha', widget=forms.PasswordInput)
    class Meta:
        model = CustomUser
        fields = ['email']
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(CustomUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class ParticipanteForm(forms.ModelForm):
    instituicao = forms.ModelChoiceField(
        queryset=Instituicao.objects.all(),
        required=False,
        label="Instituição",
        empty_label="Selecione uma instituição",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Participante
        fields = ['nome', 'sobrenome', 'CPF', 'instituicao']
        exclude = ['user']

class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['nome', 'sobrenome', 'CPF']
        exclude = ['user']

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'sobrenome', 'CPF']
        exclude = ['user']

class EventoForm(forms.ModelForm):
    atividades = forms.ModelMultipleChoiceField(
        queryset=Atividade.objects.none(),  # Inicialmente vazio
        widget=forms.CheckboxSelectMultiple,  # Usa checkboxes para seleção múltipla
        required=False,  # Não é obrigatório
    )

    class Meta:
        model = Evento
        fields = '__all__'
        exclude = ['ativo']
        widgets = {
            'data': DatePickerInput(),  # Usa o DatePickerInput para o campo 'data'
            'horario_inicio': TimePickerInput(),  # Usa o TimePickerInput para 'horario_inicio'
            'horario_fim': TimePickerInput(),  # Usa o TimePickerInput para 'horario_fim'
        }
        labels = {
            'tema': 'Tema',
            'descricao': 'Descrição',
            'data': 'Data',
            'horario_inicio': 'Horário Início',
            'horario_fim': 'Horário Fim',
            'logradouro': 'Logradouro',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'estado': 'UF',
            'banner': 'Banner',
        }

    def get_initial_data(self):
        """Retorna os valores iniciais padrão para o formulário."""
        return {
            'horario_inicio': "8:00",
            'horario_fim': "18:00",
            'logradouro': "R. Pref. Brásílio Ribas, 775",
            'bairro': "São José",
            'cidade': "Ponta Grossa",
            'estado': "Paraná",
            'banner': "https://www.lifecaretechnology.com/wp-content/uploads/2018/12/default-banner.jpg",
        }

class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = '__all__'
        exclude = ['ativo', 'data_cadastro']
        widgets = {
            'horario_inicio': TimePickerInput(),
            'horario_fim': TimePickerInput(),
        }
        labels = {
            'topico': 'Tópico',
            'descricao': 'Descrição',
            'evento': 'Evento',
            'participantes': 'Participantes',
            'alunos': 'Alunos',
            'professores': 'Professores',
            'horario_inicio': 'Horário Início',
            'horario_fim': 'Horário Fim',
        }
    def __init__(self, *args, **kwargs):
        super(AtividadeForm, self).__init__(*args, **kwargs)
        # Limita a queryset do campo "evento" apenas aos eventos ativos
        self.fields['evento'].queryset = Evento.objects.filter(ativo=True)

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        exclude = ['aluno', 'atividade', "dataAvaliacao"]

class AddParticipanteAtividadeForm(forms.Form):
    participante = forms.ModelChoiceField(queryset=Participante.objects.all(), label='Adicionar Participante')

class AddAlunoAtividadeForm(forms.Form):
    aluno = forms.ModelChoiceField(queryset=Aluno.objects.all(), label='Adicionar Aluno')

class AddProfessorAtividadeForm(forms.Form):
    professor = forms.ModelChoiceField(queryset=Professor.objects.all(), label='Adicionar Professor')

class InstituicaoForm(forms.ModelForm):
    class Meta:
        model = Instituicao
        fields = ['nome', 'telefone', 'email', 'cidade', 'estado']