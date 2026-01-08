from django.contrib import admin
from .models import Debt

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'created_at', 'updated_at', 'who_borrowed')