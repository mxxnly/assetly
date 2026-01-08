from django.db import models
from apps.core.models import BalanceItem
from apps.core.models import Transaction
class Subscription(models.Model):
    CYCLE_CHOICES = [
        ('monthly', 'Щомісяця'),
        ('yearly', 'Щороку'),
        ('weekly', 'Щотижня'),
    ]
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='subscriptions')
    from_asset = models.ForeignKey(BalanceItem, on_delete=models.CASCADE, related_name='subscriptions')

    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='UAH') 
    
    start_date = models.DateField()
    next_payment_date = models.DateField() 
    
    billing_cycle = models.CharField(max_length=10, choices=CYCLE_CHOICES, default='monthly')
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['next_payment_date']
        verbose_name = "Підписка"
        verbose_name_plural = "Підписки"

    def __str__(self):
        return f"{self.title} ({self.amount} {self.currency}) - {self.user.email}"

    @property
    def monthly_cost(self):
        if self.billing_cycle == 'yearly':
            return self.amount / 12
        elif self.billing_cycle == 'weekly':
            return self.amount * 4
        return self.amount

class Credit(models.Model):


    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='credits')
    from_asset = models.ForeignKey(BalanceItem, on_delete=models.CASCADE, related_name='credits')
    name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100, blank=True) 

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Початкова сума")
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Залишок боргу")
    currency = models.CharField(max_length=3, default='UAH')
    

    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Щомісячний платіж")
    
    start_date = models.DateField(verbose_name="Дата початку")
    end_date = models.DateField(blank=True, null=True, verbose_name="Дата погашення")
    payment_day = models.PositiveSmallIntegerField(default=1, verbose_name="День платежу (число місяця)")

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['remaining_amount']
        verbose_name = "Кредит"
        verbose_name_plural = "Кредити"

    def __str__(self):
        return f"{self.name} - Залишок: {self.remaining_amount} {self.currency}"

    @property
    def progress_percentage(self):
        if self.total_amount > 0:
            paid = self.total_amount - self.remaining_amount
            return (paid / self.total_amount) * 100
        return 0
    

class Payment(models.Model):
    TYPE_CHOICES = [
        ('subscription', 'Підписка'),
        ('credit', 'Кредит'),
    ]
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='subs_or_cred_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Платіж"
        verbose_name_plural = "Платежі"

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} {self.transaction.currency} on {self.created_at}"