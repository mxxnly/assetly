from django.contrib import admin
from .models import Portfolio, BalanceItem, Transaction, Transfer

class BalanceItemInline(admin.TabularInline):
    model = BalanceItem
    extra = 1
@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'get_total_balance')
    inlines = [BalanceItemInline]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('category', 'type', 'amount', 'created_at', 'asset')

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('from_asset', 'to_asset', 'amount', 'created_at')