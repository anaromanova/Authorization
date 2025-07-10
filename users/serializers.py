from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError
from .models import SMSCode

User = get_user_model()


class SendCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        # тут можно добавить валидацию формата номера
        return value


class VerifyCodeSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField(max_length=4)

    def validate(self, data):
        try:
            user = User.objects.get(phone=data['phone'])
        except User.DoesNotExist:
            raise ValidationError('Пользователь с таким телефоном не найден')

        cutoff = timezone.now() - timezone.timedelta(minutes=5)
        qs = SMSCode.objects.filter(
            user=user,
            code=data['code'],
            is_used=False,
            created_at__gte=cutoff
        )
        if not qs.exists():
            raise ValidationError('Неверный или просроченный код')

        # отмечаем все коды как использованные (или удаляем)
        SMSCode.objects.filter(user=user).delete()

        data['user'] = user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    invite_code = serializers.CharField(read_only=True)
    used_invite = serializers.CharField(
        source='used_invite.invite_code',
        read_only=True,
        default=''
    )
    referrals = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('phone', 'invite_code', 'used_invite', 'referrals')

    def get_referrals(self, obj):
        return list(obj.referrals.values_list('phone', flat=True))

class ApplyInviteSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)

    def validate_invite_code(self, value):
        try:
            target = User.objects.get(invite_code=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Такого инвайт-кода нет")
        return target

    def save(self, **kwargs):
        user = self.context['request'].user
        target = self.validated_data['invite_code']
        if user.used_invite:
            # нельзя перезаписать
            raise serializers.ValidationError("Вы уже активировали инвайт-код")
        user.used_invite = target
        user.save()
        return user


