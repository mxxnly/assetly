from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .models import Debt
from .forms import DebtForm

@login_required
def debt_list(request):
    """Виводить список боргів та підраховує баланс"""
    debts = Debt.objects.filter(user=request.user)
    
    total_owed_by_me = debts.filter(who_borrowed='i').aggregate(Sum('amount'))['amount__sum'] or 0
    total_owed_to_me = debts.filter(who_borrowed='other').aggregate(Sum('amount'))['amount__sum'] or 0
    
    net_balance = total_owed_to_me - total_owed_by_me

    context = {
        'debts': debts,
        'total_owed_by_me': total_owed_by_me,
        'total_owed_to_me': total_owed_to_me,
        'net_balance': net_balance,
    }
    return render(request, 'pages/debt_list.html', context)

@login_required
def debt_add(request):
    """Створює новий запис (без debt_id)"""
    if request.method == 'POST':
        form = DebtForm(request.POST)
        if form.is_valid():
            debt = form.save(commit=False)
            debt.user = request.user 
            debt.save()
            return redirect('debt_list')
    return redirect('debt_list')

@login_required
def debt_edit(request, debt_id):
    debt = get_object_or_404(Debt, id=debt_id, user=request.user)
    
    if request.method == 'POST':
        form = DebtForm(request.POST, instance=debt)
        if form.is_valid():
            form.save()
            return redirect('debt_list')
        else:
            # Цей рядок покаже вам у терміналі, чому Django не приймає дані
            print("POMYLKA REDAGUVANNYA:", form.errors)
            
    return redirect('debt_list')

@login_required
def debt_delete(request, debt_id):
    """Видаляє запис"""
    debt = get_object_or_404(Debt, id=debt_id, user=request.user)

    debt.delete()
    return redirect('debt_list')