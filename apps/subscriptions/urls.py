from django.urls import path
from .views import subscriptions_and_credits_view, add_credit, add_subscription, run_payments_view, delete_credit, delete_subscription, pay_credit
urlpatterns = [
    path('', subscriptions_and_credits_view, name='subscriptions_and_credits'),
    path('add_subscription/', add_subscription, name='add_subscription'),
    path('add_credit/', add_credit, name='add_credit'),
    path('system/run-payments/', run_payments_view, name='run_payments'),
    path('subs/delete/<int:pk>/', delete_subscription, name='delete_subscription'),
    path('credits/delete/<int:pk>/', delete_credit, name='delete_credit'),
    path('credits/pay/<int:pk>/', pay_credit, name='pay_credit'),
]