from django.urls import path
from . import views

urlpatterns = [
    path('api/auth/send-code/', views.SendCodeView.as_view(), name='send_code'),
    path('api/auth/verify-code/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('api/profile/', views.ProfileView.as_view(), name='profile'),
    path('api/profile/referrals/', views.ReferralsView.as_view(), name='referrals'),
    # ---- Простые HTML-страницы для ручного тестирования ----
    path('send-code/',  views.send_code_page,   name='send_code_page'),
    path('verify-code/',views.verify_code_page, name='verify_code_page'),
    path('profile/',    views.profile_page,     name='profile_page'),
]
