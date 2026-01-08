from django.urls import path
from . import views

urlpatterns = [
    path('', views.debt_list, name='debt_list'),
    path('add/', views.debt_add, name='debt_add'),
    path('edit/<int:debt_id>/', views.debt_edit, name='debt_edit'),
    path('delete/<int:debt_id>/', views.debt_delete, name='debt_delete'),
]