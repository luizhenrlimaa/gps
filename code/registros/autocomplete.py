from dal import autocomplete

from registros.models import Categoria, Atividade, Certificado, NivelParticipacao, Aluno


class CategoriaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Categoria.objects.filter()

        if self.q:
            qs = qs.filter(modalidades__icontains=self.q)
        return qs


class AtividadeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Atividade.objects.filter()

        if self.q:
            qs = qs.filter(descricao__icontains=self.q)
        return qs


class NivelParticipacaoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = NivelParticipacao.objects.filter()

        if self.q:
            qs = qs.filter(descricao__icontains=self.q)
        return qs


class CertificadoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Certificado.objects.filter()

        if self.q:
            qs = qs.filter(titulo__icontains=self.q)
        return qs

class AlunoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Aluno.objects.filter()

        if self.q:
            qs = qs.filter(user__first_name__icontains=self.q)
        return qs
