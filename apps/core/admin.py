from django.contrib import admin
from .models import Portfolio, BalanceItem

class BalanceItemInline(admin.TabularInline):
    model = BalanceItem
    extra = 1
@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'get_total_balance')
    inlines = [BalanceItemInline]