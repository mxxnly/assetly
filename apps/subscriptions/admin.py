from django.contrib import admin
from .models import Credit, Subscription, Payment
# Register your models here.

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'amount', 'currency', 'start_date', 'next_payment_date', 'billing_cycle', 'is_active')
    list_filter = ('user', 'billing_cycle', 'is_active')
    search_fields = ('title', 'user__email')
    date_hierarchy = 'start_date'


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'total_amount', 'remaining_amount', 'currency', 'start_date', 'end_date', 'is_active')
    list_filter = ('user', 'is_active')
    search_fields = ('name', 'user__email')
    date_hierarchy = 'start_date'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'payment_type', 'amount', 'created_at')
    list_filter = ('payment_type', 'created_at')
    search_fields = ('transaction__id',)
    date_hierarchy = 'created_at'