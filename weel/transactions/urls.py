from django.urls import path
from .views import transactions

urlpatterns = [
    path('transactions/', transactions, name='transactions'),
]
