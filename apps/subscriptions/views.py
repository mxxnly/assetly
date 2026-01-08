from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Subscription, Credit
from .forms import SubscriptionForm, CreditForm

@login_required
def subscriptions_and_credits_view(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    credits = Credit.objects.filter(user=request.user)
    
    subscription_form = SubscriptionForm()
    credit_form = CreditForm()

    context = {
        'subscriptions': subscriptions,
        'credits': credits,
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