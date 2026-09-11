from django.urls import path, re_path
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf import settings
from django.contrib.staticfiles.views import serve as static_serve


from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),

    # 👇 Dynamic Privacy Policy Pages (served from DB via admin)
    path('privacy/<str:app_name>/', views.privacy_policy, name='privacy_policy'),

    # 👇 Dynamic ads.txt (all apps in DB)
    path('app-ads.txt', views.ads_txt, name='app_ads_txt'),

    path('temporary-reset/<str:secret>/', views.temporary_password_reset, name='temporary_password_reset'),

]
