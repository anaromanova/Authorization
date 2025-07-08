from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import SMSCode

User = get_user_model()


class SendCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        # тут можно добавить валидацию формата номера
        return value


class VerifyCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=4)

    def validate(self, data):
        try:
            user = User.objects.get(phone=data['phone'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Неправильный номер")
        try:
            sms = SMSCode.objects.filter(
                user=user,
                code=data['code'],
                is_used=False,
                created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
            ).latest('created_at')
        except SMSCode.DoesNotExist:
            raise serializers.ValidationError("Код неверен или истёк")

        data['user'] = user
        data['sms_obj'] = sms
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
        return [u.phone for u in obj.referrals.all()]


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
