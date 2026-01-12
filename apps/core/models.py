from django.db import models
from django.conf import settings
from django.utils import timezone

class Portfolio(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=255, verbose_name="Назва групи")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Портфель"
        verbose_name_plural = "Портфелі"
    
    def __str__(self):
        return f"{self.name} ({self.user.email})"

    def get_total_balance(self):
        return sum(item.balance for item in self.items.all())


class BalanceItem(models.Model):

    TYPE_CHOICES = [
        ('cash', 'Готівка'),
        ('bank', 'Банківський рахунок'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='items')
    
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='bank', verbose_name="Тип коштів")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Сума")
    

    class Meta:
        unique_together = ('portfolio', 'type')
        verbose_name = "Рахунок"
        verbose_name_plural = "Рахунки"

    def __str__(self):
        return f"{self.get_type_display()}: {self.balance} (в {self.portfolio.name})"

from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва категорії")
    icon = models.CharField(max_length=50, blank=True, default='📦', verbose_name="Іконка (емодзі або клас)")
    color = models.CharField(max_length=20, blank=True, default='secondary', verbose_name="Колір (Bootstrap клас)")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('expense', 'Витрата'),
        ('income', 'Дохід'),
    ]
    
    asset = models.ForeignKey('BalanceItem', on_delete=models.CASCADE, related_name='transactions', verbose_name="Рахунок")
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name="Категорія")
    
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='expense', verbose_name="Тип")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сума")
    description = models.TextField(blank=True, verbose_name="Коментар")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата операції")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Транзакція"
        verbose_name_plural = "Транзакції"

    def __str__(self):
        sign = "-" if self.type == 'expense' else "+"
        cat_name = self.category.name if self.category else "Без категорії"
        return f"{sign}{self.amount} ({cat_name})"

    def get_ui_meta(self):

        if self.type == 'income':
            return {'icon': '💰', 'color': 'success'}
        
        if self.category:
            return {
                'icon': self.category.icon,
                'color': self.category.color
            }
            
        return {'icon': '📦', 'color': 'secondary'}
    

class Transfer(models.Model):
    from_asset = models.ForeignKey(BalanceItem, on_delete=models.CASCADE, related_name='transfers_out', verbose_name="З рахунку")
    to_asset = models.ForeignKey(BalanceItem, on_delete=models.CASCADE, related_name='transfers_in', verbose_name="На рахунок")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сума")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата переказу")
    description = models.TextField(blank=True, verbose_name="Коментар")
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Переказ"
        verbose_name_plural = "Перекази"

    @property
    def type(self):
        """Щоб шаблон розумів, що це особливий тип"""
        return 'transfer'

    @property
    def category(self):
        return 'transfer'

    def get_category_display(self):
        return "Переказ"

    def get_ui_meta(self):
        """Іконка та колір для переказу"""
        return {'icon': '⇄', 'color': 'info'}