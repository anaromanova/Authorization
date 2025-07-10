from random import randint
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils import timezone

from .models import SMSCode
from .services.sms import send_sms_code
from .serializers import (
    SendCodeSerializer, VerifyCodeSerializer,
    ProfileSerializer, ApplyInviteSerializer
)

logger = logging.getLogger(__name__)

User = get_user_model()

class SendCodeView(APIView):
    """
    POST /api/auth/send-code/  { "phone": "+7..." }
    """
    def post(self, request):
        ser = SendCodeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        phone = ser.validated_data['phone']

        User = get_user_model()
        user, _ = User.objects.get_or_create(phone=phone)
        # генерируем 4-значный код
        code = f"{randint(0,9999):04d}"
        SMSCode.objects.create(user=user, code=code)
         # отправляем через сервис
        send_sms_code(phone, code)
        return Response({"detail": "Код отправлен"}, status=status.HTTP_201_CREATED)


class VerifyCodeView(APIView):
    """
    POST /api/auth/verify-code/  { "phone": "+7...", "code": "1234" }
    """
    def post(self, request):
        ser = VerifyCodeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data['user']

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    """
    GET /api/profile/
    PATCH /api/profile/  { "invite_code": "ABC123" }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ser = ProfileSerializer(request.user)
        return Response(ser.data)

    def patch(self, request):
        ser = ApplyInviteSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(ProfileSerializer(user).data, status=status.HTTP_200_OK)


class ReferralsView(APIView):
    """
    GET /api/profile/referrals/
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        phones = request.user.referrals.values_list('phone', flat=True)
        return Response({"referrals": phones})


# --- Template (HTML) views ---

def send_code_page(request):
    """
    GET /send-code/ — страница с формой ввода телефона
    """
    return render(request, 'send_code.html')


def verify_code_page(request):
    """
    GET /verify-code/ — страница с формой ввода кода
    """
    return render(request, 'verify_code.html')


def profile_page(request):
    """
    GET /profile/ — страница профиля (показывает телефон, форму для invite-code и список рефералов)
    """
    return render(request, 'profile.html')
