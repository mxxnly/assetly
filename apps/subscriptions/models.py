from django.db import models
from apps.core.models import BalanceItem
from apps.core.models import Transaction
from dateutil.relativedelta import relativedelta
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
    

from django.core.exceptions import ValidationError

class Payment(models.Model):
    TYPE_CHOICES = [
        ('subscription', 'Підписка'),
        ('credit', 'Кредит'),
    ]
    
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='subscription')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    credit = models.ForeignKey(Credit, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Платіж по зобов'язаннях"
        verbose_name_plural = "Платежі по зобов'язаннях"

    def __str__(self):
        target = self.subscription.title if self.subscription else (self.credit.name if self.credit else "Unknown")
        return f"{self.get_payment_type_display()}: {target} - {self.amount}"

    def clean(self):
        """Перевірка: платіж має бути прив'язаний або до кредиту, або до підписки, але не до обох одразу."""
        if self.subscription and self.credit:
            raise ValidationError("Платіж не може бути одночасно і за підписку, і за кредит.")
        if not self.subscription and not self.credit:
            raise ValidationError("Виберіть підписку або кредит.")
    def calculate_next_payment_date(self):
        current_next_date = self.subscription.next_payment_date
        cycle = self.subscription.billing_cycle

        if cycle == 'monthly':
            return current_next_date + relativedelta(months=1)
        elif cycle == 'yearly':
            return current_next_date + relativedelta(years=1)
        elif cycle == 'weekly':
            return current_next_date + relativedelta(weeks=1)
        
        return current_next_date         
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        if not self.payment_type:
            if self.credit:
                self.payment_type = 'credit'
            elif self.subscription:
                self.payment_type = 'subscription'

        super().save(*args, **kwargs)

        if is_new:
            if self.credit:
                self.credit.remaining_amount -= self.amount
                if self.credit.remaining_amount < 0:
                    self.credit.remaining_amount = 0
                self.credit.save()

            if self.subscription:
                self.subscription.next_payment_date = self.calculate_next_payment_date()
                self.subscription.save()