from django.urls import path
from app_tbk import views

urlpatterns = [
    path('', views.index, name="tbk_index"),
    path('normal/', views.normal_index, name="normal"),
    path('normal/init', views.normal_init_transaction, name="normal_init"),
    path('normal/return', views.normal_return_from_webpay, name="normal_return"),
    path('normal/final', views.normal_final, name="normal_final"),
]