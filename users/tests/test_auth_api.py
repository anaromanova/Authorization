from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from users.models import User, SMSCode


class AuthAPITest(APITestCase):

    def test_send_code_creates_sms_and_user(self):
        url = reverse('send_code')
        data = {'phone': '+70000000000'}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Пользователь должен быть создан
        user = User.objects.get(phone='+70000000000')
        self.assertTrue(user)
        # И один SMSCode должен быть
        sms = SMSCode.objects.filter(user=user)
        self.assertEqual(sms.count(), 1)

    def test_verify_code_success(self):
        # Сначала создаём пользователя и код
        user = User.objects.create(phone='+71111111111')
        sms = SMSCode.objects.create(user=user, code='1234')
        url = reverse('verify_code')
        data = {'phone': '+71111111111', 'code': '1234'}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('token', resp.data)
        # Код помечен как использованный
        sms.refresh_from_db()
        self.assertTrue(sms.is_used)

    def test_verify_code_wrong_or_expired(self):
        user = User.objects.create(phone='+72222222222')
        # Код старый
        old = timezone.now() - timezone.timedelta(minutes=10)
        sms = SMSCode.objects.create(user=user, code='0000', created_at=old)
        url = reverse('verify_code')
        resp = self.client.post(url, {'phone': '+72222222222', 'code': '0000'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
