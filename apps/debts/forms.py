from .models import Debt
from django import forms

class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['amount', 'description', 'who_borrowed']
        widgets = {
            'created_at': forms.DateInput(attrs={'type': 'date'}),
        }
