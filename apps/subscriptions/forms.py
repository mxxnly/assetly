from django import forms
from .models import Subscription, Credit

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['title', 'amount','from_asset', 'currency', 'billing_cycle', 'start_date', 'next_payment_date', 'description']
        
        widgets = {
            'from_asset': forms.Select(attrs={'class': 'form-select glass-input'}),
            'title': forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'Наприклад: Netflix'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control glass-input', 'placeholder': '0.00'}),
            'currency': forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'UAH'}),
            'billing_cycle': forms.Select(attrs={'class': 'form-select glass-input'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control glass-input', 'type': 'date'}),
            'next_payment_date': forms.DateInput(attrs={'class': 'form-control glass-input', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control glass-input', 'rows': 3, 'placeholder': 'Коментар...'}),
        }
        labels = {
            'from_asset': 'Рахунок',
            'title': 'Назва сервісу',
            'amount': 'Вартість',
            'currency': 'Валюта',
            'billing_cycle': 'Періодичність',
            'start_date': 'Дата оформлення',
            'next_payment_date': 'Дата наступної оплати',
            'description': 'Нотатки'
        }

class CreditForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = [
            'name', 'bank_name', 'from_asset' , 
            'total_amount', 'remaining_amount', 'currency', 'monthly_payment', 
            'start_date', 'end_date', 'payment_day'
        ]
        
        widgets = {
            'from_asset': forms.Select(attrs={'class': 'form-select glass-input'}),
            'name': forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'Наприклад: Іпотека'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'Назва банку'}),
            
            'total_amount': forms.NumberInput(attrs={'class': 'form-control glass-input', 'placeholder': 'Початкова сума'}),
            'remaining_amount': forms.NumberInput(attrs={'class': 'form-control glass-input', 'placeholder': 'Скільки лишилось'}),
            'currency': forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'UAH'}),
            
            'monthly_payment': forms.NumberInput(attrs={'class': 'form-control glass-input', 'placeholder': 'Сума платежу'}),
            
            'start_date': forms.DateInput(attrs={'class': 'form-control glass-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control glass-input', 'type': 'date'}),
            'payment_day': forms.NumberInput(attrs={'class': 'form-control glass-input', 'min': 1, 'max': 31}),
        }
        labels = {
            'from_asset': 'Рахунок',
            'name': 'Назва кредиту',
            'bank_name': 'Банк',
            'total_amount': 'Всього взято',
            'remaining_amount': 'Залишок боргу',
            'monthly_payment': 'Платіж/міс',
            'payment_day': 'День оплати (число)',
        }