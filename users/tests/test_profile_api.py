from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from rest_framework.authtoken.models import Token


class ProfileAPITest(APITestCase):

    def setUp(self):
        # Создаём двух пользователей: A (реферальный код) и B (тот, кто применит код)
        self.user_a = User.objects.create(phone='+73333333333')
        self.user_b = User.objects.create(phone='+74444444444')
        # Генерируем токены
        self.token_b = Token.objects.create(user=self.user_b)

    def test_get_profile(self):
        url = reverse('profile')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_b.key)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Должен содержать invite_code и пустой used_invite
        self.assertIn('invite_code', resp.data)
        self.assertEqual(resp.data['used_invite'], '')

    def test_apply_invite_success(self):
        url = reverse('profile')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_b.key)
        # Б берёт код А
        data = {'invite_code': self.user_a.invite_code}
        resp = self.client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Проверяем, что used_invite установлен
        self.user_b.refresh_from_db()
        self.assertEqual(self.user_b.used_invite, self.user_a)

    def test_apply_invite_twice_forbidden(self):
        # Сначала один раз успешно
        self.user_b.used_invite = self.user_a
        self.user_b.save()
        url = reverse('profile')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_b.key)
        data = {'invite_code': self.user_a.invite_code}
        resp = self.client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_referrals_list(self):
        # Пусть B и ещё один С применят код A
        user_c = User.objects.create(phone='+75555555555')
        user_c.used_invite = self.user_a
        user_c.save()
        self.user_b.used_invite = self.user_a
        self.user_b.save()

        token_c = Token.objects.create(user=user_c)

        url = reverse('referrals')
        # Проверяем для A
        token_a = Token.objects.create(user=self.user_a)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token_a.key)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Список телефонов должен содержать B и C
        self.assertCountEqual(resp.data['referrals'], ['+74444444444', '+75555555555'])
