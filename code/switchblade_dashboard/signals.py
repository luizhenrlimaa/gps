from .models import AuditLog


def model_action_pre_save_log(sender, instance, **kwargs):

    if instance.pk:
        old_obj = sender.objects.get(pk=instance.pk)

        trace = {
            'Old data': old_obj.dict_repr(),
            'New data': instance.dict_repr()
        }

        if trace['Old data'] == trace['New data']:
            return True

        try:
            user_id = instance.modified_by.id
        except:
            user_id = None

        AuditLog.action(f'[{sender.__name__}] [UPDATE] [{instance.pk}]', obj=instance, trace=trace, user_id=user_id)

        return True


def model_action_post_save_log(sender, instance, created, **kwargs):

    if created:

        try:
            user_id = instance.modified_by.id
        except:
            user_id = None

        AuditLog.action(f'[{sender.__name__}] [CREATE] [{instance.pk}]', obj=instance, trace=instance.dict_repr(), user_id=user_id)

        return True


def model_action_delete_log(sender, instance, **kwargs):

    user_id = kwargs.get('user_id', None)

    AuditLog.action(f'[{sender.__name__}] [DELETE] [{instance.pk}]', trace=instance.dict_repr(), user_id=user_id)

    return True


def model_action_save_m2m_log(sender, instance, action, model, pk_set, **kwargs):

    if action in ['pre_add', 'pre_remove', 'pre_clear']:
        trace = {
            'Old data': instance.dict_repr(),
            'M2M': {
                'field': sender.__name__,
                'action': action.replace('pre_', '').upper(),
                'data': [str(v) for v in model.objects.filter(pk__in=pk_set).all()]
            }
        }

        try:
            user_id = instance.modified_by.id
        except:
            user_id = None

        AuditLog.action(f'[{instance.__class__.__name__}] [M2M] [{instance.pk}]', obj=instance, trace=trace, user_id=user_id)

    return True