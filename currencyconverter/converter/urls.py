from django.urls import path
from .views import ConvertCurrency

urlpatterns = [
    path('api/rates', ConvertCurrency.as_view(), name='convert_currency'),
]


