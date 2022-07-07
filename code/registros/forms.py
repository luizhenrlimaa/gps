from dal import autocomplete, forward
from django import forms

from registros.models import Categoria, Atividade, NivelParticipacao, Certificado, Submicao, SubmissaoResponse, Aluno


class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = '__all__'
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on')


class AtividadeForm(forms.ModelForm):

    class Meta:
        model = Atividade
        fields = '__all__'
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on')

class NivelParticipacaoForm(forms.ModelForm):

    class Meta:
        model = NivelParticipacao
        fields = '__all__'
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on')


class CertificadoForm(forms.ModelForm):

    #
    # categoria = forms.ModelChoiceField(widget=autocomplete.ModelSelect2(url='categoria-autocomplete'),
    #                                    queryset=Categoria.objects.filter(), required=True)
    #
    # placa = forms.ModelChoiceField(widget=autocomplete.ModelSelect2(attrs={"onchange": 'autoFillMotorista(this)'}, url='veiculo-demanda-autocomplete'),
    #                                queryset=Veiculo.objects.filter(), required=True)
    #
    # status = autocomplete.Select2ListChoiceField(
    #     choice_list=AlocacaoCarga.get_status_choice_list(),
    #     widget=autocomplete.ListSelect2(url='status-choice-list-autocomplete', forward=('tipo',))
    # )
    #
    # dedicar_frete = forms.CharField(widget=ToggleButtonInput(attrs={"onclick": 'showModal(this);'}), required=False)
    # whatsapp = forms.CharField(widget=ToggleButtonInput(attrs={"onclick": 'whatsAppMessage(this);'}), required=False)
    #
    # qtd = forms.CharField(widget=forms.HiddenInput(), required=False)
    # datas = forms.CharField(widget=forms.HiddenInput(), required=False)



    class Meta:
        model = Certificado
        fields = '__all__'
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on', 'aluno', 'horas_convertidas',)
        widgets = {
            'atividade': autocomplete.ModelSelect2(attrs={"onchange": 'autoFillAtividadeByCertificado()',
                                                      "data-placeholder": 'Selecione Primeiro a Categoria'},
                                                    url='atividade-autocomplete'),

            'nivel_participacao': autocomplete.ModelSelect2(attrs={"onchange": 'autoFillColetaEntregaByLinhaFrete()',
                                                          "data-placeholder": 'Selecione Primeiro a Atividade'},
                                                   url='participacao-autocomplete')
        }


class SubmicaoForm(forms.ModelForm):

    class Meta:
        model = Submicao
        fields = '__all__'
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on', 'aluno', 'status')

class SubmissaoResponseForm(forms.ModelForm):

    class Meta:
        model = SubmissaoResponse
        fields = '__all__'
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on', 'submicao', 'certificado')

class AlunoForm(forms.ModelForm):

    class Meta:
        model = Aluno
        fields = '__all__'
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on', 'aluno')
