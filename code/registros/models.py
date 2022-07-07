import datetime
import json
import re
import pandas as pd
from django.conf import settings
from django.contrib.gis.measure import Distance, D
from django.contrib.postgres.fields import JSONField
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.core import serializers

# Create your models here.
from django.db.models import Q, Sum, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from switchblade_dashboard.forms import DateInput
from switchblade_dashboard.models import DashboardBaseModel, DashboardBaseModelNoUser
from switchblade_users.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import fromstr, Point
from django.contrib.gis import measure

import datetime as dt

class Aluno(DashboardBaseModel):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=11)
    matricula = models.CharField(max_length=11)

    def __str__(self):
        """Unicode representation of Pais."""
        return self.user.first_name

    class Meta:
        verbose_name = _("Aluno")
        verbose_name_plural = _("Alunos")

    def get_delete_url(self):
        return reverse('aluno-delete', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('aluno-update', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('aluno-detail', kwargs={'pk': self.pk})



class Categoria(DashboardBaseModel):
    modalidades = models.CharField(max_length=80, blank=False, null=False)
    horas = models.IntegerField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        """Unicode representation of Pais."""
        return self.modalidades

    class Meta:
        verbose_name = _("Categoria")
        verbose_name_plural = _("Categorias")

    def get_delete_url(self):
        return reverse('categoria-delete', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('categoria-update', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('categoria-detail', kwargs={'pk': self.pk})



class Atividade(DashboardBaseModel):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=False, null=False)
    descricao = models.TextField(max_length=200, blank=False, null=False)
    doc_comprobatoria = models.TextField(max_length=250)

    def __str__(self):
        """Unicode representation of Pais."""
        return self.descricao

    class Meta:
        verbose_name = _("Atividade")
        verbose_name_plural = _("Atividades")

    def get_delete_url(self):
        return reverse('atividade-delete', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('atividade-update', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('atividade-detail', kwargs={'pk': self.pk})


class NivelParticipacao(DashboardBaseModel):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, blank=False, null=False)
    nivel_participacao = models.CharField(max_length=50, blank=False, null=False)
    hora_atividade = models.IntegerField()
    hora_acc = models.IntegerField()

    def __str__(self):
        """Unicode representation of Pais."""
        return self.nivel_participacao

    class Meta:
        verbose_name = _("nivel")
        verbose_name_plural = _("niveis")

    # def get_delete_url(self):
    #     return reverse('certificado-delete', kwargs={'pk': self.pk})
    #
    # def get_update_url(self):
    #     return reverse('certificado-update', kwargs={'pk': self.pk})
    #
    # def get_absolute_url(self):
    #     return reverse('certificado-detail', kwargs={'pk': self.pk})


class Certificado(DashboardBaseModel):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=False, null=False)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, blank=False, null=False)
    nivel_participacao = models.ForeignKey(NivelParticipacao, on_delete=models.CASCADE, blank=False, null=False)
    titulo = models.CharField(max_length=80, blank=False, null=False)
    descricao = models.TextField(max_length=250, blank=True, null=True)
    justificativa = models.TextField(max_length=250, blank=True, null=True)
    docfile = models.FileField(upload_to='docs', blank=True, null=True)
    total_de_horas = models.IntegerField (blank=False, null=False)
    horas_convertidas = models.FloatField(blank=True, null=True)

    def __str__(self):
        """Unicode representation of Pais."""
        return self.titulo

    class Meta:
        verbose_name = _("certificado")
        verbose_name_plural = _("certificados")

    def get_delete_url(self):
        return reverse('certificado-delete', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('certificado-update', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('certificado-detail', kwargs={'pk': self.pk})

    # def save(self, *args, **kwargs):
    #     self.usuario = args.user
    #     nivel = NivelParticipacao.objects.filter(pk=self.nivel_participacao.pk)
    #     horas = ((self.total_horas/nivel.hora_atividade)*nivel.hora_acc)
    #     self.horas_convertidas = horas
    #     super().save(*args, **kwargs)

class Submicao(DashboardBaseModel):

    SUBTETIDO = 1
    EM_ANALISE = 2
    APROVADO = 3
    REPROVADO = 4

    STATUS_CHOICES = (
        (SUBTETIDO, 'Submetido'),
        (EM_ANALISE, 'Em Analise'),
        (APROVADO, 'Aprovado'),
        (REPROVADO, 'Reprovado'),
    )
    
    certificados = models.ManyToManyField(Certificado, blank=False, null=False)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, blank=False, null=False)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, blank=True, null=True)


    def get_delete_url(self):
        return reverse('submicao-aluno-delete', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('submicao-aluno-update', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('submicao-aluno-detail', kwargs={'pk': self.pk})


class SubmissaoResponse(DashboardBaseModel):
    submissao = models.ForeignKey(Submicao, on_delete=models.CASCADE, blank=False, null=False)
    certificado = models.ForeignKey(Certificado, on_delete=models.CASCADE, blank=False, null=False)
    is_ok = models.BooleanField(default=False, blank=False, null=False)
    observacao = models.TextField(max_length=250, blank=True, null=True)

    # def get_delete_url(self):
    #     return reverse('link-order-wallet-delete', kwargs={'pk': self.pk})
    #
    # def get_update_url(self):
    #     return reverse('link-order-wallet-update', kwargs={'pk': self.pk})
    #
    # def get_absolute_url(self):
    #     return reverse('link-order-wallet-detail', kwargs={'pk': self.pk})

