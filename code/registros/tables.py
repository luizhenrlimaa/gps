from django_tables2 import columns

from registros.models import Categoria, Atividade, NivelParticipacao, Certificado, Submicao, SubmissaoResponse, Aluno
from switchblade_dashboard import tables as dashboard_table

class CategoriaTable(dashboard_table.Table):

    class Meta(dashboard_table.Table.Meta):
        model = Categoria
        fields = ['modalidades', 'horas',]
        exclude = ('select_row', )


class AtividadeTable(dashboard_table.Table):

    class Meta(dashboard_table.Table.Meta):
        model = Atividade
        fields = ['categoria', 'descricao', 'nivel_participacao',]
        exclude = ('select_row',)

class NivelParticipacaoTable(dashboard_table.Table):

    class Meta(dashboard_table.Table.Meta):
        model = NivelParticipacao
        fields = []
        exclude = ('select_row', )


class CertificadoTable(dashboard_table.Table):

    class Meta(dashboard_table.Table.Meta):
        model = Certificado
        fields = ['titulo', 'categoria', 'atividade', 'total_de_horas', 'horas_convertidas',]
        exclude = ('select_row',)

class SubmicaoTable(dashboard_table.Table):

    actions_custom = columns.TemplateColumn(template_name='registros/table-action-req-aluno.html',
                                     verbose_name='Ações',
                                     attrs={
                                         "th": {
                                             "style": 'width: 75px'
                                         },
                                     },
                                     orderable=False,
                                     exclude_from_export=True)


    class Meta(dashboard_table.Table.Meta):
        model = Submicao
        fields = ['actions_custom','aluno', 'status']
        exclude = ('select_row', 'certificados', 'actions')

class SubmissaoResponseTable(dashboard_table.Table):

    class Meta(dashboard_table.Table.Meta):
        model = SubmissaoResponse
        fields = ['submissao', 'certificado', 'is_ok']
        exclude = ('select_row', )

class SubmissaoSecretariaTable(dashboard_table.Table):

    actions_custom = columns.TemplateColumn(template_name='registros/table-action-req-secretaria.html',
                                     verbose_name='Ações',
                                     attrs={
                                         "th": {
                                             "style": 'width: 75px'
                                         },
                                     },
                                     orderable=False,
                                     exclude_from_export=True)

    class Meta(dashboard_table.Table.Meta):
        model = Submicao
        fields = ['actions_custom','aluno', 'status']
        exclude = ('select_row', 'actions',)

class AlunoTable(dashboard_table.Table):

    class Meta(dashboard_table.Table.Meta):
        model = Aluno
        fields = ['user__first_name', 'matricula']
        exclude = ('select_row', )
