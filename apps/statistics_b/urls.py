from django.urls import path
from . import views

urlpatterns = [
    path('by-category/', views.stat_by_category, name='stat_by_category'),
    path('transactions/', views.trans_and_pay_view, name='stat_transactions')
]