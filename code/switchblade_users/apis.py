from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status, serializers, generics
import base64
from django.core.files.base import ContentFile


class UserUpdateAvatarAPI(APIView):

    # authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):

        try:
            user = request.user
            file = request.data.get('data', None)
            image_data = file
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr))
            file_name = f"{user.id}.{ext}"
            user.avatar.save(file_name, data, save=True)

            messages.success(request, "Avatar successfully updated")

            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

