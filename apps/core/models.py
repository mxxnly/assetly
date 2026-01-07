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

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('expense', 'Витрата'),
        ('income', 'Дохід'),
    ]
    
    CATEGORY_CHOICES = [
        ('food', 'Їжа та продукти'),
        ('transport', 'Транспорт і пальне'),
        ('entertainment', 'Розваги'),
        ('utilities', 'Комунальні'),
        ('shopping', 'Шопінг'),
        ('apartment', 'Дім та оренда'),
        ('transfer', 'Переказ'),
        ('salary', 'Зарплата'),
        ('other', 'Інше'),
    ]

    asset = models.ForeignKey(BalanceItem, on_delete=models.CASCADE, related_name='transactions', verbose_name="Рахунок")
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='expense', verbose_name="Тип")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="other", verbose_name="Категорія")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сума")
    description = models.TextField(blank=True, verbose_name="Коментар")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата операції")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Транзакція"
        verbose_name_plural = "Транзакції"

    def __str__(self):
        sign = "-" if self.type == 'expense' else "+"
        return f"{sign}{self.amount} ({self.get_category_display()})"

    # --- МЕТОД SAVE ВИДАЛЕНО, ЩОБ НЕ БУЛО ПОДВІЙНОГО СПИСАННЯ ---

    def get_ui_meta(self):
        """
        Повертає іконку та колір для відображення в шаблоні.
        """
        if self.type == 'income':
            return {'icon': '💰', 'color': 'success'}
        
        mapping = {
            'food':          {'icon': '🍔', 'color': 'warning'},
            'transport':     {'icon': '⛽', 'color': 'info'},
            'entertainment': {'icon': '🎬', 'color': 'danger'},
            'utilities':     {'icon': '💡', 'color': 'primary'},
            'shopping':      {'icon': '🛍️', 'color': 'info'},
            'apartment':     {'icon': '🏠', 'color': 'primary'},
            'transfer':      {'icon': '💸', 'color': 'secondary'},
            'salary':        {'icon': '💵', 'color': 'success'},
            'other':         {'icon': '📦', 'color': 'secondary'},
        }
        return mapping.get(self.category, {'icon': '📦', 'color': 'secondary'})
    

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