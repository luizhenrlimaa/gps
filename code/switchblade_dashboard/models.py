from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _


import re


class DashboardBaseModel(models.Model):

    # Automatic
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="%(class)s_informer", on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="%(class)s_updater", on_delete=models.PROTECT)
    modified_on = models.DateTimeField(auto_now=True)

    # class AuthManager(models.Manager):
    #     def allowed(self, user):
    #         qs = super().get_queryset().filter()
    #
    #         from libs.permissions.permissions import get_allowed_product_lines, get_allowed_accounts
    #         allowed_accounts = get_allowed_accounts(user, ids=True)
    #         if allowed_accounts:
    #             qs = qs.filter(account__pk__in=allowed_accounts)
    #
    #         allowed_product_lines = get_allowed_product_lines(user, ids=True)
    #         if allowed_product_lines:
    #             qs = qs.filter(product_line__pk__in=allowed_product_lines)
    #
    #         return qs
    #
    # objects = AuthManager()

    class Meta:
        abstract = True

    def get_delete_url(self):
        model_name = re.sub('(?!^)([A-Z]+)', r'-\1', self._meta.object_name).lower()
        return reverse(f"{model_name}-delete", kwargs={'pk': self.pk})

    def get_update_url(self):
        model_name = re.sub('(?!^)([A-Z]+)', r'-\1', self._meta.object_name).lower()
        return reverse(f"{model_name}-update", kwargs={'pk': self.pk})

    def get_absolute_url(self):
        model_name = re.sub('(?!^)([A-Z]+)', r'-\1', self._meta.object_name).lower()
        return reverse(f"{model_name}-detail", kwargs={'pk': self.pk})


class DashboardBaseModelNoUser(models.Model):

    # Automatic
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_delete_url(self):
        model_name = re.sub('(?!^)([A-Z]+)', r'-\1', self._meta.object_name).lower()
        return reverse(f"{model_name}-delete", kwargs={'pk': self.pk})

    def get_update_url(self):
        model_name = re.sub('(?!^)([A-Z]+)', r'-\1', self._meta.object_name).lower()
        return reverse(f"{model_name}-update", kwargs={'pk': self.pk})

    def get_absolute_url(self):
        model_name = re.sub('(?!^)([A-Z]+)', r'-\1', self._meta.object_name).lower()
        return reverse(f"{model_name}-detail", kwargs={'pk': self.pk})


class AuditLog(DashboardBaseModelNoUser):

    LEVEL_DEBUG = 'DEBUG'
    LEVEL_ACTION = 'ACTION'
    LEVEL_ACCESS = 'ACCESS'
    LEVEL_INFO = 'INFO'
    LEVEL_WARNING = 'WARNING'
    LEVEL_ERROR = 'ERROR'
    LEVEL_CRITICAL = 'CRITICAL'

    LEVEL_CHOICES = (
        (LEVEL_DEBUG, 'DEBUG'),
        (LEVEL_ACTION, 'ACTION'),
        (LEVEL_ACCESS, 'ACCESS'),
        (LEVEL_INFO, 'INFO'),
        (LEVEL_WARNING, 'WARNING'),
        (LEVEL_ERROR, 'ERROR'),
        (LEVEL_CRITICAL, 'CRITICAL'),
    )

    LEVEL_COLOR = {
        LEVEL_DEBUG: 'black',
        LEVEL_ACTION: 'lightseagreen',
        LEVEL_ACCESS: 'silver',
        LEVEL_INFO: 'blue',
        LEVEL_WARNING: 'orange',
        LEVEL_ERROR: 'red',
        LEVEL_CRITICAL: 'purple',
    }

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default=LEVEL_DEBUG)
    msg = models.TextField(verbose_name=_('Message'))
    trace = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='User', on_delete=models.DO_NOTHING, blank=True, null=True)
    
    class Meta:
        ordering = ('-created_on',)
    
    def __str__(self):
        return self.msg
    
    @classmethod
    def _save_log(cls, msg, level=LEVEL_DEBUG, trace=None, user_id=None, obj=None):
        
        cls.objects.create(level=level, msg=msg, trace=trace, created_by_id=user_id, content_object=obj)
    
    @classmethod
    def debug(cls, msg, trace=None, user_id=None, obj=None):
        
        cls._save_log(msg, cls.LEVEL_DEBUG, trace=trace, user_id=user_id, obj=obj)

    @classmethod
    def access(cls, msg, trace=None, user_id=None, obj=None):
        
        cls._save_log(msg, cls.LEVEL_ACCESS, trace=trace, user_id=user_id, obj=obj)

    @classmethod
    def info(cls, msg, trace=None, user_id=None, obj=None):
        
        cls._save_log(msg, cls.LEVEL_INFO, trace=trace, user_id=user_id, obj=obj)

    @classmethod
    def warning(cls, msg, trace=None, user_id=None, obj=None):
        
        cls._save_log(msg, cls.LEVEL_WARNING, trace=trace, user_id=user_id, obj=obj)

    @classmethod
    def error(cls, msg, trace=None, user_id=None, obj=None):
        
        cls._save_log(msg, cls.LEVEL_ERROR, trace=trace, user_id=user_id, obj=obj)

    @classmethod
    def critical(cls, msg, trace=None, user_id=None, obj=None):
        
        cls._save_log(msg, cls.LEVEL_CRITICAL, trace=trace, user_id=user_id, obj=obj)

    @classmethod
    def action(cls, msg, trace=None, user_id=None, obj=None):

        cls._save_log(msg, cls.LEVEL_ACTION, trace=trace, user_id=user_id, obj=obj)
