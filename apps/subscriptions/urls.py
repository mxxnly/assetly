from django.urls import path
from .views import subscriptions_and_credits_view, add_credit, add_subscription
urlpatterns = [
    path('', subscriptions_and_credits_view, name='subscriptions_and_credits'),
    path('add_subscription/', add_subscription, name='add_subscription'),
    path('add_credit/', add_credit, name='add_credit'),
]