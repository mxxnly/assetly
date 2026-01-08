from django.db import models


class Debt(models.Model):

    WHO_BORROWED_CHOICES = [
        ('i', 'Я'),
        ('other', 'Інший')
    ]

    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    who_borrowed = models.CharField(max_length=10, choices=WHO_BORROWED_CHOICES)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Заборгованість"
        verbose_name_plural = "Заборгованості"

    def __str__(self):
        return f"Debt of {self.amount} by {self.user}"
