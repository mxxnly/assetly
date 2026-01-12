from django.shortcuts import render
from apps.core.models import Transaction, Category, Portfolio, BalanceItem, Transfer
from apps.debts.models import Debt
from apps.subscriptions.models import Credit, Payment, Subscription
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

@login_required
def stat_by_category(request):
    categories = Category.objects.all()
    user_assets = BalanceItem.objects.filter(portfolio__user=request.user)

    selected_assets = request.GET.getlist('assets')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    data = []
    
    for c in categories:
        transactions = Transaction.objects.filter(category=c, asset__portfolio__user=request.user)

        if selected_assets:
            transactions = transactions.filter(asset_id__in=selected_assets)

        if start_date:
            transactions = transactions.filter(created_at__date__gte=start_date)
        if end_date:
            transactions = transactions.filter(created_at__date__lte=end_date)

        total_plus = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_minus = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        if total_plus > 0 or total_minus > 0:
            data.append({
                "name": c.name,
                "icon": c.icon,
                "color": c.color,
                "income": total_plus,
                "expense": total_minus,
                "difference": total_plus - total_minus
            })

    context = {
        'data': data,
        'user_assets': user_assets,
        'selected_assets': list(map(int, selected_assets)),
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'pages/stat_by_category.html', context)


@login_required
def trans_and_pay_view(request):
    selected_assets = request.GET.getlist('assets') 
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    user_assets = BalanceItem.objects.filter(portfolio__user=request.user)

    transactions = Transaction.objects.filter(asset__portfolio__user=request.user).order_by('-created_at')
    payments = Payment.objects.filter(subscription__user=request.user).order_by('-created_at')


    if selected_assets:
        transactions = transactions.filter(asset_id__in=selected_assets)
        payments = payments.filter(transaction__asset_id__in=selected_assets)

    if start_date:
        transactions = transactions.filter(created_at__date__gte=start_date)
        payments = payments.filter(created_at__date__gte=start_date)

    if end_date:
        transactions = transactions.filter(created_at__date__lte=end_date)
        payments = payments.filter(created_at__date__lte=end_date)

    context = {
        'transactions': transactions,
        'payments': payments,
        'user_assets': user_assets,
        'selected_assets': list(map(int, selected_assets)),
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'pages/trans_and_pay.html', context)