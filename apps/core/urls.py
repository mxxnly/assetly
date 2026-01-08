from django.urls import path
from .views import home, portfolio_detail, transaction_delete, transaction_update, portfolio_update, transaction_add, balance_item_add, transfer_add, transfer_delete, create_portfolio
urlpatterns = [
    path('', home, name='home'),
    path('portfolio/<int:portfolio_id>/', portfolio_detail, name='portfolio_detail'),
    path('transaction/<int:pk>/delete/', transaction_delete, name='transaction_delete'),
    path('transaction/<int:pk>/update/', transaction_update, name='transaction_update'),
    path('portfolio/<int:portfolio_id>/transaction/add/', transaction_add, name='transaction_add'),
    path('portfolio/<int:portfolio_id>/update/', portfolio_update, name='portfolio_update'),
    path('portfolio/<int:portfolio_id>/balance_item/add/', balance_item_add, name='balance_item_add'),
    path('portfolio/<int:portfolio_id>/transfer/add/', transfer_add, name='transfer_add'),
    path('transfer/<int:transfer_id>/delete/', transfer_delete, name='transfer_delete'),
    path('portfolio/create/', create_portfolio, name='create_portfolio'),
]