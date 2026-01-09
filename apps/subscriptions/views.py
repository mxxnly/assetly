from django.contrib.auth.decorators import login_required
from .models import Subscription, Credit
from .forms import SubscriptionForm, CreditForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from apps.core.models import BalanceItem, Transaction, Category, Portfolio
from django.utils import timezone
from .models import Payment
@login_required
def delete_subscription(request, pk):
    sub = get_object_or_404(Subscription, pk=pk, user=request.user)
    if request.method == 'POST':
        sub.delete()
        messages.success(request, "Підписку видалено.")
    return redirect('subscriptions_and_credits')

@login_required
def delete_credit(request, pk):
    credit = get_object_or_404(Credit, pk=pk, user=request.user)
    if request.method == 'POST':
        credit.delete()
        messages.success(request, "Кредит видалено.")
    return redirect('subscriptions_and_credits')

@login_required
def pay_credit(request, pk):
    credit = get_object_or_404(Credit, pk=pk, user=request.user)
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        asset_id = request.POST.get('asset_id')
        asset = get_object_or_404(BalanceItem, pk=asset_id, portfolio__user=request.user)
        
        if amount <= 0:
            messages.error(request, "Сума має бути більше нуля.")
            return redirect('subscriptions_and_credits')

        if asset.balance < amount:
            messages.error(request, "Недостатньо коштів на рахунку.")
            return redirect('subscriptions_and_credits')
            
        try:
            with transaction.atomic():
                asset.balance -= amount
                asset.save()
                
                cat_credits, _ = Category.objects.get_or_create(
                    name="Кредити", 
                    defaults={'icon': '🏦', 'color': 'warning'}
                )

                new_transaction = Transaction.objects.create(
                    asset=asset,
                    amount=amount,
                    type='expense', 
                    category=cat_credits, 
                    description=f"Погашення кредиту: {credit.name}",
                    created_at=timezone.now() 
                )
                Payment.objects.create(
                    transaction=new_transaction,
                    credit=credit,
                    amount=amount,
                    payment_type='credit'
                )
                
            messages.success(request, f"Внесено {amount} {credit.currency} в рахунок кредиту.")
            
        except Exception as e:
            messages.error(request, f"Помилка при оплаті: {e}")
            
    return redirect('subscriptions_and_credits')

@login_required
def subscriptions_and_credits_view(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    credits = Credit.objects.filter(user=request.user)
    
    user_portfolios = Portfolio.objects.filter(user=request.user)
    subscription_form = SubscriptionForm()
    credit_form = CreditForm()

    context = {
        'subscriptions': subscriptions,
        'credits': credits,
        'user_portfolios': user_portfolios,
        'subscription_form': subscription_form,
        'credit_form': credit_form,
    }
    return render(request, 'pages/subscription_and_credit_list.html', context)
@login_required
def add_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            return redirect('subscriptions_and_credits')
    return redirect('subscriptions_and_credits')

@login_required
def add_credit(request):
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            credit = form.save(commit=False)
            credit.user = request.user
            credit.save()
            return redirect('subscriptions_and_credits')
    return redirect('subscriptions_and_credits')

import re
from io import StringIO
from django.core.management import call_command

@login_required 
def run_payments_view(request):
    logs = None
    
    if request.method == 'POST':
        out = StringIO()
        
        try:
            call_command(
                'process_payments', 
                user=request.user.id,
                stdout=out, 
                no_color=True
            )
            raw_logs = out.getvalue()
        except Exception as e:
            raw_logs = f"Критична помилка при запуску: {str(e)}"
            
        out.close()
        logs = raw_logs.split('\n')

    return render(request, 'pages/run_payments.html', {'logs': logs})