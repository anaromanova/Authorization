from django.shortcuts import render
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .models import SMSCode
from .serializers import (
    SendCodeSerializer, VerifyCodeSerializer,
    ProfileSerializer, ApplyInviteSerializer
)

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
        from random import randint
        code = f"{randint(0,9999):04d}"
        SMSCode.objects.create(user=user, code=code)
        # эмуляция отправки и задержка
        # time.sleep(randint(1,2))
        print(f"[DEBUG] send SMS to {phone}: {code}")
        return Response({"detail": "Код отправлен"}, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    """
    POST /api/auth/verify-code/  { "phone": "+7...", "code": "1234" }
    """
    def post(self, request):
        ser = VerifyCodeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        phone = ser.validated_data['phone']
        code  = ser.validated_data['code']

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Пользователь с таким телефоном не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # код жив только 5 минут
        cutoff = timezone.now() - timezone.timedelta(minutes=5)

        sms_qs = SMSCode.objects.filter(
            user=user,
            code=code,
            is_used=False,
            created_at__gte=cutoff
        ).order_by('-created_at')

        if not sms_qs.exists():
            return Response(
                {'detail': 'Неверный или просроченный код'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sms = sms_qs.first()
        sms.is_used = True
        sms.save(update_fields=['is_used'])

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
        phones = [u.phone for u in request.user.referrals.all()]
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
