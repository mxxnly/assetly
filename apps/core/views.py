import decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Portfolio, BalanceItem, Transaction, Transfer, Category
from django.views.decorators.http import require_POST
from .forms import TransactionForm, PortfolioForm, BalanceItemForm, CategoryForm
from itertools import chain
from operator import attrgetter
from django.db.models import Q
from django.db import transaction
from django.db.models import F
from apps.subscriptions.models import Credit
from apps.subscriptions.models import Payment
from django.db import transaction as db_transaction 
@login_required 
def home(request):
    portfolios = Portfolio.objects.filter(user=request.user).prefetch_related('items')

    total_wealth = BalanceItem.objects.filter(portfolio__user=request.user).aggregate(total=Sum('balance'))['total'] or 0

    total_credits_amount_remaining = Credit.objects.filter(user=request.user).aggregate(total=Sum('remaining_amount'))['total'] or 0

    context = {
        'portfolios': portfolios,
        'total_wealth': total_wealth,
        'total_credits_amount_remaining': total_credits_amount_remaining,
        
    }
    return render(request, 'pages/home.html', context)
def portfolio_detail(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    categories = Category.objects.all()
    transactions = Transaction.objects.filter(asset__portfolio=portfolio)
    
    transfers = Transfer.objects.filter(
        Q(from_asset__portfolio=portfolio) | Q(to_asset__portfolio=portfolio)
    )

    combined_history = sorted(
        chain(transactions, transfers), 
        key=attrgetter('created_at'), 
        reverse=True
    )
    
    existing_types = list(portfolio.items.values_list('type', flat=True))

    user_portfolios = Portfolio.objects.filter(user=request.user).prefetch_related('items')

    context = {
        'portfolio': portfolio,
        'transactions': combined_history,
        'existing_types': existing_types,
        'user_portfolios': user_portfolios,
        'categories': categories,
    }
    return render(request, 'pages/portfolio_detail.html', context)

@transaction.atomic
def transfer_delete(request, transfer_id):
    transfer = get_object_or_404(Transfer, id=transfer_id)
    
    if transfer.from_asset.portfolio.user != request.user:
        return redirect('home')
        
    if request.method == 'POST':
        
        BalanceItem.objects.filter(id=transfer.from_asset_id).update(
            balance=F('balance') + transfer.amount
        )
        
        BalanceItem.objects.filter(id=transfer.to_asset_id).update(
            balance=F('balance') - transfer.amount
        )
        
        portfolio_id = transfer.from_asset.portfolio.id
        transfer.delete()
        
        return redirect('portfolio_detail', portfolio_id=portfolio_id)
        
    return redirect('home')

def balance_item_add(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        form = BalanceItemForm(request.POST, portfolio=portfolio)
        if form.is_valid():
            item = form.save(commit=False)
            item.portfolio = portfolio
            item.save()
            return redirect('portfolio_detail', portfolio_id=portfolio.id)
            
    return redirect('portfolio_detail', portfolio_id=portfolio.id)

def transaction_add(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.asset = portfolio.items.get(id=request.POST.get('asset_id'))
            
            if transaction.type == 'income':
                transaction.asset.balance += transaction.amount
            else:
                transaction.asset.balance -= transaction.amount
            
            transaction.asset.save()
            transaction.save()
            
            return redirect('portfolio_detail', portfolio_id=portfolio.id)
    
    return redirect('portfolio_detail', portfolio_id=portfolio.id)

@login_required
@require_POST
def transaction_delete(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, asset__portfolio__user=request.user)
    portfolio_id = tx.asset.portfolio.id

    try:
        with db_transaction.atomic():
            if tx.type == 'income':
                tx.asset.balance -= tx.amount
            else:
                tx.asset.balance += tx.amount
            
            tx.asset.save()

            payment = Payment.objects.filter(transaction=tx).first()

            if payment:
                if payment.credit:
                    payment.credit.remaining_amount += payment.amount
                    payment.credit.save()
                
                payment.delete()

            tx.delete()

    except Exception as e:
        print(f"Помилка при видаленні: {e}")

    return redirect('portfolio_detail', portfolio_id=portfolio_id)

def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, asset__portfolio__user=request.user)
    
    old_amount = transaction.amount
    old_type = transaction.type
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            if old_type == 'income':
                transaction.asset.balance -= old_amount
            else:
                transaction.asset.balance += old_amount
            
            new_trans = form.save(commit=False)
            
            if new_trans.type == 'income':
                transaction.asset.balance += new_trans.amount
            else:
                transaction.asset.balance -= new_trans.amount
            
            transaction.asset.save()
            new_trans.save()
            
            return redirect('portfolio_detail', portfolio_id=transaction.asset.portfolio.id)
    
    return redirect('portfolio_detail', portfolio_id=transaction.asset.portfolio.id)

def portfolio_update(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            form.save()
            return redirect('portfolio_detail', portfolio_id=portfolio.id)
            
    return redirect('portfolio_detail', portfolio_id=portfolio.id)

def transfer_add(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    if request.method == 'POST':

        from_asset_id = request.POST.get('from_asset')
        to_asset_id = request.POST.get('to_asset')
        amount = float(request.POST.get('amount'))
        description = request.POST.get('description')
        created_at = request.POST.get('created_at')

        from_asset = get_object_or_404(BalanceItem, id=from_asset_id, portfolio__user=request.user)
        to_asset = get_object_or_404(BalanceItem, id=to_asset_id, portfolio__user=request.user)

        if from_asset == to_asset:
            return redirect('portfolio_detail', portfolio_id=portfolio.id)

        transfer = Transfer(
            from_asset=from_asset,
            to_asset=to_asset,
            amount=amount,
            description=description
        )
        if created_at:
            transfer.created_at = created_at
            
        from_asset.balance -= decimal.Decimal(amount)
        from_asset.save()
        
        to_asset.balance += decimal.Decimal(amount) # Конвертуємо float в decimal, якщо треба
        to_asset.save()
        
        transfer.save()
            
        return redirect('portfolio_detail', portfolio_id=portfolio.id)
            
    return redirect('portfolio_detail', portfolio_id=portfolio.id)


@login_required
def create_portfolio(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            return redirect('portfolio_detail', portfolio_id=portfolio.id)
    else:
        form = PortfolioForm()
    return render(request, 'pages/portfolio_form.html', {'form': form})

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CategoryForm()
    return render(request, 'pages/category_form.html', {'form': form})