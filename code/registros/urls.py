from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.generic import TemplateView

from registros.autocomplete import CategoriaAutocomplete, AtividadeAutocomplete, CertificadoAutocomplete, \
    NivelParticipacaoAutocomplete, AlunoAutocomplete
from registros.models import NivelParticipacao
from registros.views import CategoriaList, CategoriaCreate, CategoriaDetail, CategoriaUpdate, CategoriaDelete, \
    AtividadeList, AtividadeCreate, AtividadeDetail, AtividadeUpdate, AtividadeDelete, CertificadoList, \
    CertificadoCreate, CertificadoDetail, CertificadoUpdate, CertificadoDelete, AtividadeByCertificado, \
    SubmicaoCreate, RegistraSubmissao, Timeline, SubmissaoResponseList, \
    SubmissaoResponseCreate, SubmissaoResponseDetail, SubmissaoResponseUpdate, SubmissaoResponseDelete, \
    AnalisarSubmissao, VizualizarErros, SubmicaoAlunoList, SubmicaoAlunoDetail, SubmicaoAlunoUpdate, \
    SubmicaoAlunoDelete, SubmissaoSecretariaList, AlunoList, AlunoCreate, AlunoDetail, AlunoUpdate, AlunoDelete, \
    OpenFile
from switchblade_dashboard.decorators import register_resource
from switchblade_dashboard.views import DashboardIndexView


urlpatterns = [

    path('registros/', include([
        path('', register_resource(
            DashboardIndexView.as_view(page_title='Registros', header='Registros', columns=[3, 3, 3, 3])), name='registros-dashboard'),

        path('categoria/', include([
            path('', register_resource(CategoriaList), name='categoria-list'),
            path('cadastro/', register_resource(CategoriaCreate), name='categoria-create'),
            path('detalhe/<int:pk>', register_resource(CategoriaDetail), name='categoria-detail'),
            path('edicao/<int:pk>', register_resource(CategoriaUpdate), name='categoria-update'),
            path('remocao/<int:pk>', register_resource(CategoriaDelete), name='categoria-delete'),
            path('autocomplete/', login_required(CategoriaAutocomplete.as_view()), name='categoria-autocomplete'),
        ])),

        path('atividade/', include([
            path('', register_resource(AtividadeList), name='atividade-list'),
            path('cadastro/', register_resource(AtividadeCreate), name='atividade-create'),
            path('detalhe/<int:pk>', register_resource(AtividadeDetail), name='atividade-detail'),
            path('edicao/<int:pk>', register_resource(AtividadeUpdate), name='atividade-update'),
            path('remocao/<int:pk>', register_resource(AtividadeDelete), name='atividade-delete'),
            path('autocomplete/', login_required(AtividadeAutocomplete.as_view()), name='atividade-autocomplete'),
            path('nivel_pacriticipacao_autocomplete/', login_required(NivelParticipacaoAutocomplete.as_view()), name='participacao-autocomplete')
        ])),

    ])),


    path('submissao/', include([
        path('', register_resource(
            DashboardIndexView.as_view(page_title='Submissão', header='Submissão', columns=[3, 3, 3, 3])),
             name='submissao-dashboard'),

        path('submissao-aluno/', include([
            path('', register_resource(SubmicaoAlunoList), name='submicao-aluno-list'),
            path('cadastro/', register_resource(SubmicaoCreate), name='submicao-aluno-create'),
            path('detalhe/<int:pk>', register_resource(SubmicaoAlunoDetail), name='submicao-aluno-detail'),
            path('edicao/<int:pk>', register_resource(SubmicaoAlunoUpdate), name='submicao-aluno-update'),
            path('remocao/<int:pk>', register_resource(SubmicaoAlunoDelete), name='submicao-aluno-delete'),
            path('register-sub/<int:pk>', register_resource(RegistraSubmissao), name='register-sub'),
            path('timeline/<int:pk>', register_resource(Timeline), name='time-line'),
            path('vizualizar-erros/<int:pk>', register_resource(VizualizarErros), name='vizualizar-erros')
            # path('autocomplete/', login_required(SubmicaoAutocomplete.as_view()), name='submicao-autocomplete'),
        ])),

        path('submicao-secretaria/', include([
            path('', register_resource(SubmissaoSecretariaList), name='submicao-list'),
            # path('autocomplete/', login_required(SubmicaoAutocomplete.as_view()), name='submicao-autocomplete'),
        ])),

        path('submissao-resposta/', include([
            path('', register_resource(SubmissaoResponseList), name='submissao-response-list'),
            path('cadastro/', register_resource(SubmissaoResponseCreate), name='submissao-response-create'),
            path('detalhe/<int:pk>', register_resource(SubmissaoResponseDetail), name='submissao-response-detail'),
            path('edicao/<int:pk>', register_resource(SubmissaoResponseUpdate), name='submissao-response-update'),
            path('remocao/<int:pk>', register_resource(SubmissaoResponseDelete), name='submissao-response-delete'),
            path('analisar/<int:pk>', register_resource(AnalisarSubmissao), name='analisar-submissao')
            # path('autocomplete/', login_required(SubmissaoResponseAutocomplete.as_view()), name='submissao-response-autocomplete'),
        ])),

    ])),

        path('aluno/', include([
            path('', register_resource(AlunoList), name='aluno-list'),
            path('cadastro/', register_resource(AlunoCreate), name='aluno-create'),
            path('detalhe/<int:pk>', register_resource(AlunoDetail), name='aluno-detail'),
            path('edicao/<int:pk>', register_resource(AlunoUpdate), name='aluno-update'),
            path('remocao/<int:pk>', register_resource(AlunoDelete), name='aluno-delete'),
            path('autocomplete/', login_required(AlunoAutocomplete.as_view()), name='aluno-autocomplete'),
        ])),


    path('certificados/', include([
        path('', register_resource(
            DashboardIndexView.as_view(page_title='Certificados', header='Certificados', columns=[3, 3, 3, 3])),
             name='certificados-dashboard'),

        path('gestao/', include([
            path('', register_resource(CertificadoList), name='certificado-list'),
            path('cadastro/', register_resource(CertificadoCreate), name='certificado-create'),
            path('detalhe/<int:pk>', register_resource(CertificadoDetail), name='certificado-detail'),
            path('edicao/<int:pk>', register_resource(CertificadoUpdate), name='certificado-update'),
            path('remocao/<int:pk>', register_resource(CertificadoDelete), name='certificado-delete'),
            path('autocomplete/', login_required(CertificadoAutocomplete.as_view()), name='certificado-autocomplete'),
            path('auto_fill_atividade/',login_required(AtividadeByCertificado), name='autoFillAtividade'),
            path('vizualizar-documento/<int:pk>', login_required(OpenFile), name='vizualiza-certificado')
        ])),
    ])),
]