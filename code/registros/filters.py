import django_filters
from dal import autocomplete

from registros.models import Categoria, Atividade, Certificado, Submicao, SubmissaoResponse, Aluno


class CategoriaFilter(django_filters.FilterSet):

    class Meta:
        model = Categoria
        fields = {
            'modalidades': ['icontains'],
        }

class AtividadeFilter(django_filters.FilterSet):

    class Meta:
        model = Atividade
        fields = {
            'descricao': ['icontains'],
        }

class CertificadoFilter(django_filters.FilterSet):

    class Meta:
        model = Certificado
        fields = {
            'titulo': ['icontains'],
        }

class SubmicaoFilter(django_filters.FilterSet):

    class Meta:
        model = Submicao
        fields = {
            'aluno__user__first_name': ['icontains'],
        }

class SubmissaoResponseFilter(django_filters.FilterSet):

    class Meta:
        model = SubmissaoResponse
        fields = {
            'is_ok': ['icontains'],
        }

class AlunoFilter(django_filters.FilterSet):

    class Meta:
        model = Aluno
        fields = {
            'user__first_name': ['icontains'],
        }
