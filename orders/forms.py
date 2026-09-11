from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        # Нам нужны только имя и телефон для быстрой связи и СБП
        fields = ['first_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'style': 'width: 100%; padding: 12px; border-radius: 4px; border: 1px solid #eae6e1; font-size: 16px; margin-bottom: 20px;',
                'placeholder': 'Иван'
            }),
            'phone': forms.TextInput(attrs={
                'style': 'width: 100%; padding: 12px; border-radius: 4px; border: 1px solid #eae6e1; font-size: 16px; margin-bottom: 20px;',
                'placeholder': '+7 (999) 000-00-00'
            }),
        }
