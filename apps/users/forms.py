from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control-custom'
            
        self.fields['email'].widget.attrs['placeholder'] = 'name@company.com'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Іван'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Петренко'
class CustomAuthenticationForm(AuthenticationForm):
    """
    Форма входу. Тут нам треба вручну додати стилі до полів username та password.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Стилізація поля Email (username)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control-custom',
            'placeholder': 'name@example.com'
        })

        # Стилізація поля Пароль
        self.fields['password'].widget.attrs.update({
            'class': 'form-control-custom',
            'placeholder': '••••••••'
        })