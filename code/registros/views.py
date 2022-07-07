from urllib import request
import datetime as dt

from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from requests import Response
from rest_framework import status

from registros.filters import CategoriaFilter, AtividadeFilter, CertificadoFilter, SubmicaoFilter, \
    SubmissaoResponseFilter, AlunoFilter
from registros.forms import CategoriaForm, AtividadeForm, NivelParticipacaoForm, CertificadoForm, SubmicaoForm, \
    SubmissaoResponseForm, AlunoForm
from registros.models import Categoria, Atividade, NivelParticipacao, Certificado, Submicao, SubmissaoResponse, Aluno
from registros.tables import CategoriaTable, AtividadeTable, CertificadoTable, SubmicaoTable, SubmissaoResponseTable, \
    SubmissaoSecretariaTable, AlunoTable
from switchblade_dashboard.forms import TabularFormSetHelper
from switchblade_dashboard.views import DashboardListView, DashboardDeleteView, DashboardUpdateView, DashboardCreateView, \
    DashboardDetailView
from switchblade_users.models import User


class CategoriaList(DashboardListView):

    page_title = 'Categoria'
    header = 'Categoria'

    show_export_button = False
    add_button_title = 'Cadastrar Categoria'
    add_button_url = reverse_lazy('categoria-create')

    table_class = CategoriaTable
    filter_class = CategoriaFilter
    object = Categoria

    def get_queryset(self):
        qs = Categoria.objects.filter()
        return qs


class CategoriaDetail(DashboardDetailView):

    page_title = 'Categoria'
    header = 'Categoria'
    object = Categoria

    rows_based_on_form = CategoriaForm

    def get_queryset(self):
        qs = Categoria.objects.filter()
        return qs


class CategoriaCreate(DashboardCreateView):

    page_title = 'Categoria'
    header = 'Cadastro de Categoria'

    form_class = CategoriaForm
    object = Categoria

    show_button_save_continue = True
    owner_include = True

    success_message = 'Categoria cadastrado com sucesso.'

    success_redirect = 'categoria-list'


class CategoriaUpdate(DashboardUpdateView):

    page_title = 'Categoria'
    header = 'Edição de Categoria'

    form_class = CategoriaForm
    object = Categoria

    success_message = 'Categoria editado com sucesso.'
    success_redirect = 'categoria-list'

    def get_queryset(self):
        qs = Categoria.objects.filter()
        return qs


class CategoriaDelete(DashboardDeleteView):

    header = 'Remoção de Categoria'

    object = Categoria
    validate_owner = False

    success_message = 'Categoria removido com sucesso.'
    success_redirect = 'categoria-list'

    def get_queryset(self):
        qs = Categoria.objects.filter()
        return qs


class AtividadeList(DashboardListView):

    page_title = 'Atividade'
    header = 'Atividade'

    show_export_button = False
    add_button_title = 'Cadastrar Atividade'
    add_button_url = reverse_lazy('atividade-create')

    table_class = AtividadeTable
    filter_class = AtividadeFilter
    object = Atividade

    def get_queryset(self):
        qs = Atividade.objects.filter()
        return qs


class AtividadeDetail(DashboardDetailView):

    page_title = 'Atividade'
    header = 'Atividade'
    object = Atividade

    rows_based_on_form = AtividadeForm

    def get_queryset(self):
        qs = Atividade.objects.filter()
        return qs


class AtividadeCreate(DashboardCreateView):

    page_title = 'Atividade'
    header = 'Cadastro de Atividade'

    form_class = AtividadeForm
    object = Atividade

    show_button_save_continue = True
    owner_include = True


    inlines = [
        {
            'title': "Nivel Participacao",
            'model': NivelParticipacao,
            'form': NivelParticipacaoForm,
            'helper': TabularFormSetHelper,
            'owner_include': True
        },
    ]


    success_message = 'Atividade cadastrado com sucesso.'

    success_redirect = 'atividade-list'


class AtividadeUpdate(DashboardUpdateView):

    page_title = 'Atividade'
    header = 'Edição de Atividade'

    form_class = AtividadeForm
    object = Atividade

    success_message = 'Atividade editado com sucesso.'
    success_redirect = 'atividade-list'

    def get_queryset(self):
        qs = Atividade.objects.filter()
        return qs


class AtividadeDelete(DashboardDeleteView):

    header = 'Remoção de Atividade'

    object = Atividade
    validate_owner = False

    success_message = 'Atividade removido com sucesso.'
    success_redirect = 'atividade-list'

    def get_queryset(self):
        qs = Atividade.objects.filter()
        return qs

class CertificadoList(DashboardListView):

    page_title = 'Certificado'
    header = 'Certificado'

    show_export_button = False
    add_button_title = 'Cadastrar Certificado'
    add_button_url = reverse_lazy('certificado-create')

    table_class = CertificadoTable
    filter_class = CertificadoFilter
    object = Certificado

    def get_queryset(self):
        qs = Certificado.objects.filter(aluno__user=self.request.user)
        return qs


class CertificadoDetail(DashboardDetailView):

    page_title = 'Certificado'
    header = 'Certificado'
    object = Certificado

    rows_based_on_form = CertificadoForm

    def get_queryset(self):
        qs = Certificado.objects.filter(aluno__user=self.request.user)
        return qs


class CertificadoCreate(DashboardCreateView):

    page_title = 'Certificado'
    header = 'Cadastro de Certificado'

    form_class = CertificadoForm
    object = Certificado

    show_button_save_continue = True
    owner_include = True

    success_message = 'Certificado cadastrado com sucesso.'

    success_redirect = 'certificado-list'

    def post(self, request, pk=None, *args, **kwargs):

        form = self.get_form(request)

        if form.is_valid():

            obj = form.save(commit=False)
            with transaction.atomic():
                obj.aluno = Aluno.objects.get(user=self.request.user)
                nivel = NivelParticipacao.objects.filter(pk=obj.nivel_participacao.pk).first()
                horas = ((float(obj.total_de_horas)/float(nivel.hora_atividade))*float(nivel.hora_acc))
                obj.horas_convertidas = horas
                obj.created_by = self.request.user
                obj.modified_by = self.request.user
                obj.created_on = dt.datetime.now()
                obj.modified_on = dt.datetime.now()
                obj.save()

            return redirect(self.success_redirect)
# def CertificadoCreate(request):
#     template_name = 'registros/form_create.html'
#
#     return render(request, template_name)


class CertificadoUpdate(DashboardUpdateView):

    page_title = 'Certificado'
    header = 'Edição de Certificado'

    form_class = CertificadoForm
    object = Certificado

    success_message = 'Certificado editado com sucesso.'
    success_redirect = 'certificado-list'

    def get_queryset(self):
        qs = Certificado.objects.filter(aluno__user=self.request.user)
        return qs


class CertificadoDelete(DashboardDeleteView):

    header = 'Remoção de Certificado'

    object = Certificado
    validate_owner = False

    success_message = 'Certificado removido com sucesso.'
    success_redirect = 'certificado-list'

    def get_queryset(self):
        qs = Certificado.objects.filter(usuario=self.request.user)
        return qs

def AtividadeByCertificado():

    # authentication_classes = (authentication.TokenAuthentication,)

    if request.is_ajax and request.method == 'GET':
        result = {}
        pk = request.GET['pk']
        if pk == '':
            return Response(data=result, status=status.HTTP_200_OK)

        obj = Categoria.objects.filter(pk=pk).first()
        if obj:

            atv = Atividade.objects.filter(categoria=obj)

            # result = {
            #     'pk': obj.pk,
            #     'cidade_coleta_pk': atv.pk,
            #     'atv_nome': atv.descricao,
            #     'atv_disabled': True,
            # }

        return HttpResponse(data=atv)

class SubmicaoAlunoList(DashboardListView):

    page_title = 'Submicao'
    header = 'Submicao'

    show_export_button = False
    add_button_title = 'Cadastrar Submicao'
    add_button_url = reverse_lazy('submicao-aluno-create')

    table_class = SubmicaoTable
    filter_class = SubmicaoFilter
    object = Submicao

    def get_queryset(self):
        qs = Submicao.objects.filter()
        return qs


class SubmicaoAlunoDetail(DashboardDetailView):

    page_title = 'Submicao'
    header = 'Submicao'
    object = Submicao

    rows_based_on_form = SubmicaoForm

    def get_queryset(self):
        qs = Submicao.objects.filter()
        return qs

def SubmicaoCreate(request):
    template_name = 'registros/submicao-create.html'

    user = request.user

    todos_certificados = Certificado.objects.filter(aluno__user=user)

    context = {
        'todos_certificados' : todos_certificados,
        'aluno' : user,
    }

    return render(request, template_name, context)

def RegistraSubmissao(request, pk):


    if request.method == 'POST':
        user = User.objects.get(pk=int(pk))
        list = request.POST.getlist('selected')

        nova_submicao = None
        nova_submicao = Submicao()
        nova_submicao.aluno = Aluno.objects.get(user=user)
        nova_submicao.status = 1
        nova_submicao.created_by = request.user
        nova_submicao.modified_by = request.user
        nova_submicao.created_on = dt.datetime.now()
        nova_submicao.modified_on = dt.datetime.now()
        nova_submicao.save()

        for i in list:
            certificado = Certificado.objects.get(pk=int(i))
            nova_submicao.certificados.add(certificado)

    return redirect('submicao-aluno-list')


# class SubmicaoCreate(DashboardCreateView):
#
#     page_title = 'Submicao'
#     header = 'Cadastro de Submicao'
#
#     form_class = SubmicaoForm
#     object = Submicao
#
#     show_button_save_continue = True
#     owner_include = True
#
#     success_message = 'Submicao cadastrada com sucesso.'
#
#     success_redirect = 'submicao-list'


class SubmicaoAlunoUpdate(DashboardUpdateView):

    page_title = 'Submicao'
    header = 'Edição de Submicao'

    form_class = SubmicaoForm
    object = Submicao

    success_message = 'Submicao editada com sucesso.'
    success_redirect = 'submicao-aluno-list'

    def get_queryset(self):
        qs = Submicao.objects.filter()
        return qs


class SubmicaoAlunoDelete(DashboardDeleteView):

    header = 'Remoção de Submicao'

    object = Submicao
    validate_owner = False

    success_message = 'Submicao removida com sucesso.'
    success_redirect = 'submicao-aluno-list'

    def get_queryset(self):
        qs = Submicao.objects.filter()
        return qs

def Timeline(request, pk):

    template_name = 'registros/timeline.html'
    submicao = Submicao.objects.get(pk=int(pk))

    i = submicao.created_on.strftime('%d %b')
    m = submicao.modified_on.strftime('%d %b')
    f = None
    resp = SubmissaoResponse.objects.filter(submissao=submicao)

    if resp:
        f = resp[0].created_on.strftime('%d %b')


    context = {
        'sub' : submicao,
        'submetido_data': i,
        'em_analise_data' : m,
        'final' : f
    }

    return render(request, template_name, context)

class SubmissaoResponseList(DashboardListView):

    page_title = 'Resposta da Submissão'
    header = 'Resposta da Submissão'

    show_export_button = False
    add_button_title = 'Cadastrar Resposta da Submissao'
    add_button_url = reverse_lazy('submissao-response-create')

    table_class = SubmissaoResponseTable
    filter_class = SubmissaoResponseFilter
    object = SubmissaoResponse

    def get_queryset(self):
        qs = SubmissaoResponse.objects.filter()
        return qs


class SubmissaoResponseDetail(DashboardDetailView):

    page_title = 'Resposta da Submissao'
    header = 'Resposta da Submissao'
    object = SubmissaoResponse

    rows_based_on_form = SubmissaoResponseForm

    def get_queryset(self):
        qs = SubmissaoResponse.objects.filter()
        return qs


class SubmissaoResponseCreate(DashboardCreateView):

    page_title = 'Resposta da Submissao'
    header = 'Cadastro de Resposta da Submissao'

    form_class = SubmissaoResponseForm
    object = SubmissaoResponse

    show_button_save_continue = True
    owner_include = True

    success_message = 'Resposta da Submissao cadastrado com sucesso.'

    success_redirect = 'submissao-response-list'


class SubmissaoResponseUpdate(DashboardUpdateView):

    page_title = 'Resposta da Submissao'
    header = 'Edição de Resposta da Submissao'

    form_class = SubmissaoResponseForm
    object = SubmissaoResponse

    success_message = 'Resposta da Submissao editado com sucesso.'
    success_redirect = 'submissao-response-list'

    def get_queryset(self):
        qs = SubmissaoResponse.objects.filter()
        return qs


class SubmissaoResponseDelete(DashboardDeleteView):

    header = 'Remoção de Resposta da Submissao'

    object = SubmissaoResponse
    validate_owner = False

    success_message = 'Resposta da Submissao removido com sucesso.'
    success_redirect = 'submissao-response-list'

    def get_queryset(self):
        qs = SubmissaoResponse.objects.filter()
        return qs

def AnalisarSubmissao(request, pk):

    submissao = Submicao.objects.get(pk=int(pk))
    context = {}

    if request.method == 'POST':

        deferido = request.POST.getlist('deferido')
        indeferido = request.POST.getlist('indeferido')
        observacao = request.POST.getlist('obs')
        i = 0

        for elemento in deferido:
            novo_deferido = None
            novo_deferido = SubmissaoResponse()
            novo_deferido.submissao = submissao
            novo_deferido.certificado = Certificado.objects.get(pk=int(elemento))
            novo_deferido.is_ok = True
            novo_deferido.observacao = '-'
            novo_deferido.created_by = request.user
            novo_deferido.modified_by = request.user
            novo_deferido.created_on = dt.datetime.now()
            novo_deferido.modified_on = dt.datetime.now()
            novo_deferido.save()
            i += 1

        for elemento in indeferido:
            novo_indeferido = None
            novo_indeferido = SubmissaoResponse()
            novo_indeferido.submissao = submissao
            novo_indeferido.certificado = Certificado.objects.get(pk=int(elemento))
            novo_indeferido.is_ok = False
            novo_indeferido.observacao = observacao[i]
            novo_indeferido.created_by = request.user
            novo_indeferido.modified_by = request.user
            novo_indeferido.created_on = dt.datetime.now()
            novo_indeferido.modified_on = dt.datetime.now()
            novo_indeferido.save()
            i += 1

        if len(indeferido) >= 1:
            submissao.status = 4
            submissao.save()

        elif len(deferido) >= 1:
            submissao.status = 3
            submissao.save()

        return redirect('submissao-response-list')
    else:
        submissao.status = 2
        submissao.save()
        template_name = 'registros/analise-submissao.html'
        context = {
            'sub' : submissao,
            # 'certificados' : submissao.certificado
        }
        return render(request, template_name, context)

def VizualizarErros(request, pk):


    respostas = SubmissaoResponse.objects.filter(submissao__pk=int(pk), is_ok=False)
    template_name = 'registros/vizualizar_problemas.html'

    context = {
        'resp' : respostas,
    }
    return render(request, template_name, context)

class SubmissaoSecretariaList(DashboardListView):

    page_title = 'Submissao Secretaria'
    header = 'Submissao Secretaria'

    show_export_button = False
    add_button_title = 'Cadastrar Submissao'
    add_button_url = reverse_lazy('submissão-create')

    table_class = SubmissaoSecretariaTable
    filter_class = SubmicaoFilter
    object = Submicao

    def get_queryset(self):
        qs = Submicao.objects.filter(Q(status=1) | Q(status=2))
        return qs

class AlunoList(DashboardListView):

    page_title = 'Aluno'
    header = 'Aluno'

    show_export_button = False
    add_button_title = 'Cadastrar Aluno'
    add_button_url = reverse_lazy('aluno-create')

    table_class = AlunoTable
    filter_class = AlunoFilter
    object = Aluno

    def get_queryset(self):
        qs = Aluno.objects.filter()
        return qs


class AlunoDetail(DashboardDetailView):

    page_title = 'Aluno'
    header = 'Aluno'
    object = Aluno

    rows_based_on_form = AlunoForm

    def get_queryset(self):
        qs = Aluno.objects.filter()
        return qs


class AlunoCreate(DashboardCreateView):

    page_title = 'Aluno'
    header = 'Cadastro de Aluno'

    form_class = AlunoForm
    object = Aluno

    show_button_save_continue = True
    owner_include = True

    success_message = 'Aluno cadastrado com sucesso.'

    success_redirect = 'aluno-list'


class AlunoUpdate(DashboardUpdateView):

    page_title = 'Aluno'
    header = 'Edição de Aluno'

    form_class = AlunoForm
    object = Aluno

    success_message = 'Aluno editado com sucesso.'
    success_redirect = 'aluno-list'

    def get_queryset(self):
        qs = Aluno.objects.filter()
        return qs


class AlunoDelete(DashboardDeleteView):

    header = 'Remoção de Aluno'

    object = Aluno
    validate_owner = False

    success_message = 'Aluno removido com sucesso.'
    success_redirect = 'aluno-list'

    def get_queryset(self):
        qs = Aluno.objects.filter()
        return qs

def OpenFile(request, pk):

    certificado = Certificado.objects.get(pk=int(pk))
    documento = open(certificado.docfile.path, 'rb')

    return FileResponse(documento)