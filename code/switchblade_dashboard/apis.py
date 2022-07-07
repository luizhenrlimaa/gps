from celery.result import AsyncResult
from django.template.loader import render_to_string
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class CeleryTaskStatusAPI(APIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):

        task_id = request.query_params.get('task_id', None)
        revoke = request.query_params.get('revoke', None)

        if task_id:

            celery_task = AsyncResult(task_id)
            if revoke is not None:
                celery_task.revoke(terminate=True)

            return Response(status=status.HTTP_200_OK, data={'state': celery_task.state})

        return Response(status=status.HTTP_400_BAD_REQUEST)


class MenuHelpAPI(APIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):

        try:
            slug = request.query_params.get('slug', None)
            if slug:
                text = render_to_string(f'menu_help/{slug}.html')

                return Response(status=status.HTTP_200_OK, data=text)

            return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
