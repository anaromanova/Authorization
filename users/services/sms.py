import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def send_sms_code(phone: str, code: str) -> None:
    """
    Функция отправки СМС-кода.
    В зависимости от флага USE_REAL_SMS_SERVICE либо шлёт реальный код,
    либо логирует его в отладку.
    """
    if getattr(settings, 'USE_REAL_SMS_SERVICE', False):
        # TODO: тут интеграция с реальным SMS-провайдером
        pass
    else:
        logger.debug('Sms code for %s is %s', phone, code)