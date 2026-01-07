from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Portfolio, BalanceItem

@login_required 
def home(request):
    portfolios = Portfolio.objects.filter(user=request.user).prefetch_related('items')

    total_wealth = BalanceItem.objects.filter(portfolio__user=request.user).aggregate(total=Sum('balance'))['total'] or 0

    context = {
        'portfolios': portfolios,
        'total_wealth': total_wealth,
    }
    return render(request, 'pages/home.html', context)

def portfolio_detail(request, portfolio_id):
    portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
    context = {
        'portfolio': portfolio
    }
    return render(request, 'pages/portfolio_detail.html', context)