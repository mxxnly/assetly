from django.db import models
from django.conf import settings

class Portfolio(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=255, verbose_name="Назва групи")
    created_at = models.DateTimeField(auto_now_add=True)

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

    def __str__(self):
        return f"{self.get_type_display()}: {self.balance} (в {self.portfolio.name})"