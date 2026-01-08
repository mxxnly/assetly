from django import forms
from .models import Transaction, Portfolio, BalanceItem, Transfer, Category

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'created_at', 'description']
        widgets = {
            'created_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control-custom'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control-custom'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control-custom'}),
            'type': forms.Select(attrs={'class': 'form-control-custom'}),
            'category': forms.Select(attrs={'class': 'form-control-custom'}),
        }

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control-custom'}),
        }
        labels = {
            'name': 'Назва портфоліо',
        }

class BalanceItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.portfolio = kwargs.pop('portfolio', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = BalanceItem
        fields = ['type', 'balance']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control-custom'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control-custom', 'placeholder': '0.00'}),
        }

    def clean_type(self):
        type_val = self.cleaned_data['type']
        
        if self.portfolio and BalanceItem.objects.filter(portfolio=self.portfolio, type=type_val).exists():
            raise forms.ValidationError(f"Рахунок типу '{self.get_instance_type_display(type_val)}' вже існує в цьому портфоліо.")
        
        return type_val

    def get_instance_type_display(self, type_val):
        return dict(BalanceItem.TYPE_CHOICES).get(type_val, type_val)
    

class TransferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.portfolio = kwargs.pop('portfolio', None)
        super().__init__(*args, **kwargs)
        
        if self.portfolio:
            self.fields['from_asset'].queryset = BalanceItem.objects.filter(portfolio=self.portfolio)
            self.fields['to_asset'].queryset = BalanceItem.objects.filter(portfolio=self.portfolio)

    class Meta:
        model = Transfer
        fields = ['from_asset', 'to_asset', 'amount', 'created_at', 'description']
        widgets = {
            'from_asset': forms.Select(attrs={'class': 'form-control-custom'}),
            'to_asset': forms.Select(attrs={'class': 'form-control-custom'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control-custom', 'placeholder': '0.00'}),
            'created_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control-custom'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control-custom'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        from_asset = cleaned_data.get('from_asset')
        to_asset = cleaned_data.get('to_asset')

        if from_asset and to_asset and from_asset == to_asset:
            raise forms.ValidationError("Не можна робити переказ на той самий рахунок.")
        
        return cleaned_data
    

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'icon': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Емодзі або клас іконки'}),
            'color': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Bootstrap клас кольору'}),
        }